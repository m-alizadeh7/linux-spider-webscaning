"""AI Reporter utilities

Provides a simple adapter to call configured AI providers (OpenAI, OpenRouter, Gemini)
by reading a small INI-style configuration file. Produces expert analysis in Persian (Farsi)
based on a scan report content passed as context.

Config example (see config/ai_services.txt.example):
[gemini]
api_key=your-api-key
model=gemini-2.5-flash
temperature=0.2
"""
from __future__ import annotations

import configparser
import json
import os
import time
from pathlib import Path
from typing import Dict, Optional, Any

import requests


def read_config(path: str) -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    cfg.read(path)
    return cfg


def _call_openai(api_key: str, model: str, prompt: str, temperature: float = 0.2) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 4000,
    }
    resp = requests.post(url, headers=headers, json=data, timeout=120)
    resp.raise_for_status()
    j = resp.json()
    return j["choices"][0]["message"]["content"].strip()


def _call_openrouter(api_key: str, model: str, prompt: str, temperature: float = 0.2) -> str:
    url = "https://api.openrouter.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    resp = requests.post(url, headers=headers, json=data, timeout=120)
    resp.raise_for_status()
    j = resp.json()
    return j["choices"][0]["message"]["content"].strip()


def _call_gemini(api_key: str, model: str, prompt: str, temperature: float = 0.2) -> str:
    # Default to latest flash model if generic name given
    if model in ["gemini-v1", "gemini", "gemini-1.5-flash", ""]:
        model = "gemini-2.0-flash"
    
    # Try multiple API versions
    api_versions = ["v1beta", "v1"]
    last_error = None
    
    for version in api_versions:
        try:
            url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": api_key}
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 8192
                }
            }
            resp = requests.post(url, headers=headers, params=params, json=data, timeout=180)
            
            if resp.status_code == 403:
                # Try alternative model
                if "2.5" in model:
                    alt_model = model.replace("2.5", "2.0")
                    url = f"https://generativelanguage.googleapis.com/{version}/models/{alt_model}:generateContent"
                    resp = requests.post(url, headers=headers, params=params, json=data, timeout=180)
            
            resp.raise_for_status()
            j = resp.json()
            
            if "candidates" in j and isinstance(j["candidates"], list):
                candidate = j["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    return "".join(p.get("text", "") for p in parts).strip()
            return json.dumps(j)
            
        except requests.exceptions.HTTPError as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            continue
    
    if last_error:
        raise last_error
    return ""


def call_provider(kind: str, api_key: str, model: str, prompt: str, temperature: float = 0.2) -> str:
    kind = kind.lower()
    if kind == "openai":
        return _call_openai(api_key, model, prompt, temperature)
    if kind == "openrouter":
        return _call_openrouter(api_key, model, prompt, temperature)
    if kind == "gemini":
        return _call_gemini(api_key, model, prompt, temperature)
    raise ValueError(f"Unsupported provider: {kind}")


def load_prompt_template(analysis_type: str = "general") -> str:
    """Load the appropriate prompt template"""
    prompts_dir = Path("config/prompts")
    prompt_file = prompts_dir / "ai_analysis_prompt.txt"
    
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    
    # Default prompt if file not found
    return """شما یک متخصص ارشد امنیت وب و سئو هستید.
بر اساس گزارش اسکن زیر، یک تحلیل کامل به زبان فارسی ارائه دهید.
شامل: خلاصه اجرایی، تحلیل امنیتی، تحلیل سئو، و چک‌لیست اقدامات."""


def build_analysis_prompt(report_text: str, analysis_type: str = "general", 
                          target_type: str = "own") -> str:
    """Build the full prompt for AI analysis
    
    Args:
        report_text: The scan report content
        analysis_type: Type of analysis (general, competitor, own)
        target_type: Whether analyzing own site or competitor
    """
    base_prompt = load_prompt_template(analysis_type)
    
    # Add context based on target type
    if target_type == "competitor":
        context = """
## نوع تحلیل: تحلیل سایت رقیب
- نقاط قوت رقیب را شناسایی کنید
- نقاط ضعف قابل بهره‌برداری را مشخص کنید
- استراتژی رقابتی پیشنهادی ارائه دهید
- فرصت‌های سئو نسبت به رقیب را بیان کنید
"""
    else:
        context = """
## نوع تحلیل: تحلیل سایت خودی
- مشکلات را با اولویت‌بندی دقیق مشخص کنید
- راه‌حل عملی برای هر مشکل ارائه دهید
- چک‌لیست اجرایی برای تیم فنی تهیه کنید
"""
    
    full_prompt = f"""{base_prompt}

{context}

---

## گزارش اسکن:

{report_text}

---

لطفاً تحلیل خود را به زبان فارسی و در قالب Markdown ارائه دهید.
"""
    return full_prompt


def generate_ai_report_from_text(report_text: str, config_path: str = "config/ai_services.txt",
                                  analysis_type: str = "general", 
                                  target_type: str = "own") -> Dict[str, Any]:
    """Generate AI analysis from scan report text
    
    Args:
        report_text: The scan report content
        config_path: Path to AI services configuration
        analysis_type: Type of analysis
        target_type: 'own' for own site, 'competitor' for competitor analysis
    
    Returns:
        Dict mapping provider -> result or error
    """
    results: Dict[str, Any] = {}
    
    if not os.path.exists(config_path):
        results["error"] = f"فایل پیکربندی یافت نشد: {config_path}"
        return results
    
    cfg = read_config(config_path)
    prompt = build_analysis_prompt(report_text, analysis_type, target_type)
    
    for section in cfg.sections():
        try:
            kind = section
            api_key = cfg.get(section, "api_key", fallback="").strip()
            model = cfg.get(section, "model", fallback="gemini-2.5-flash").strip()
            temp = cfg.getfloat(section, "temperature", fallback=0.3)
            
            if not api_key:
                results[section] = {"error": "api_key not configured"}
                continue
            
            print(f"    ⏳ در حال تحلیل با {section}...")
            text = call_provider(kind, api_key, model, prompt, temperature=temp)
            results[section] = {"result": text}
            print(f"    ✓ تحلیل {section} کامل شد")
            
            # Be polite to APIs
            time.sleep(1)
            
        except Exception as e:
            results[section] = {"error": str(e)}
            print(f"    ✗ خطا در {section}: {e}")
    
    return results


def save_aggregated_report(results: Dict[str, Any], domain: str, 
                           out_dir: str = "reports",
                           target_type: str = "own") -> str:
    """Save AI analysis results to a markdown file"""
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    
    analysis_label = "competitor" if target_type == "competitor" else "own"
    out_path = os.path.join(out_dir, f"ai_analysis_{domain}_{analysis_label}_{ts}.md")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# 🕷️ گزارش تحلیل هوشمند - {domain}\n\n")
        f.write(f"📅 تاریخ: {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"🔍 نوع تحلیل: {'سایت رقیب' if target_type == 'competitor' else 'سایت خودی'}\n\n")
        f.write("---\n\n")
        
        for provider, res in results.items():
            if provider == "error":
                f.write(f"⚠️ خطا: {res}\n\n")
                continue
                
            f.write(f"## 🤖 تحلیل توسط: {provider.upper()}\n\n")
            
            if isinstance(res, dict) and "result" in res:
                f.write(res["result"] + "\n\n")
            else:
                f.write(f"خطا: {json.dumps(res, ensure_ascii=False)}\n\n")
            
            f.write("---\n\n")
        
        f.write("\n---\n")
        f.write("*تولید شده توسط Linux Spider Web Scanner*\n")
        f.write("*https://github.com/m-alizadeh7/linux-spider-webscaning*\n")
    
    return out_path
