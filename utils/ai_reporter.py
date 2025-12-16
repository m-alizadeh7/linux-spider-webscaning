"""AI Reporter utilities

Provides a simple adapter to call configured AI providers (OpenAI, OpenRouter, Gemini stub)
by reading a small INI-style configuration file. Produces bilingual (EN + FA) expert analysis
based on a scan report content passed as context.

Config example (see ai_services.txt.example):
[openai]
api_key=sk-...
model=gpt-4o-mini
temperature=0.2

Each section will be called in order. If a provider call fails it will be skipped.
"""
from __future__ import annotations

import configparser
import json
import os
import time
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
        "max_tokens": 1500,
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    j = resp.json()
    # Best-effort parse
    return j["choices"][0]["message"]["content"].strip()


def _call_openrouter(api_key: str, model: str, prompt: str, temperature: float = 0.2) -> str:
    # OpenRouter exposes an OpenAI-compatible endpoint for many models
    url = f"https://api.openrouter.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    resp = requests.post(url, headers=headers, json=data, timeout=60)
    resp.raise_for_status()
    j = resp.json()
    return j["choices"][0]["message"]["content"].strip()


def _call_gemini(api_key: str, model: str, prompt: str, temperature: float = 0.2) -> str:
    # Gemini API v1beta with generateContent endpoint
    # Supports models like: gemini-2.5-flash, gemini-2.5-pro, gemini-1.5-flash
    if model in ["gemini-v1", "gemini", "gemini-1.5-flash"]:
        model = "gemini-2.5-flash"  # Default to latest flash model
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 4096
        }
    }
    resp = requests.post(url, headers=headers, params=params, json=data, timeout=120)
    resp.raise_for_status()
    j = resp.json()
    # Extract text from Gemini response
    if "candidates" in j and isinstance(j["candidates"], list):
        candidate = j["candidates"][0]
        if "content" in candidate and "parts" in candidate["content"]:
            parts = candidate["content"]["parts"]
            return "".join(p.get("text", "") for p in parts).strip()
    return json.dumps(j)


def call_provider(kind: str, api_key: str, model: str, prompt: str, temperature: float = 0.2) -> str:
    kind = kind.lower()
    if kind == "openai":
        return _call_openai(api_key, model, prompt, temperature)
    if kind == "openrouter":
        return _call_openrouter(api_key, model, prompt, temperature)
    if kind == "gemini":
        return _call_gemini(api_key, model, prompt, temperature)
    raise ValueError(f"Unsupported provider: {kind}")


def build_bilingual_prompt(base_prompt: str) -> str:
    """Wrap the base prompt to require high-quality expert analysis in English and Persian.

    The AI should output two clearly separated sections: English analysis and Persian analysis.
    """
    wrapper = (
        "You are an expert web security and SEO analyst. "
        "Given the following scan report content, produce a detailed, technical, and actionable analysis. "
        "Output MUST include two sections clearly marked: 'English Analysis' and 'Persian Analysis'.\n\n"
    )
    follow = (
        "Requirements:\n"
        "- Provide concise executive summary (1-2 paragraphs).\n"
        "- Provide detailed findings with evidence and recommended remediation steps.\n"
        "- Include classification of severity (Critical/High/Medium/Low).\n"
        "- Provide follow-up checks and automated tests to validate fixes.\n"
        "- Ensure text is suitable to be appended to the scan report and to be used in automated workflows.\n"
        "- Write the English section in professional technical English and the Persian section in formal Persian (Farsi).\n\n"
    )
    # Encourage resilience to future changes
    extensibility = (
        "Note: write the analysis so it remains useful as this tool evolves: avoid referencing transient internal filenames or implementation details; instead reference observable facts from the report."
    )
    return f"{wrapper}{base_prompt}\n\n{follow}{extensibility}"


def generate_ai_report_from_text(report_text: str, config_path: str = "ai_services.txt") -> Dict[str, Any]:
    """Read configuration and call configured providers to generate AI analyses.

    Returns a dict mapping provider -> text result or error message.
    """
    results: Dict[str, Any] = {}
    if not os.path.exists(config_path):
        results["error"] = f"Config file not found: {config_path}"
        return results

    cfg = read_config(config_path)
    base_prompt = report_text
    prompt = build_bilingual_prompt(base_prompt)

    for section in cfg.sections():
        try:
            kind = section
            api_key = cfg.get(section, "api_key", fallback="").strip()
            model = cfg.get(section, "model", fallback="gpt-4o-mini").strip()
            temp = cfg.getfloat(section, "temperature", fallback=0.2)
            if not api_key:
                results[section] = {"error": "api_key not set in config"}
                continue
            text = call_provider(kind, api_key, model, prompt, temperature=temp)
            results[section] = {"result": text}
            # be polite to APIs
            time.sleep(1)
        except Exception as e:
            results[section] = {"error": str(e)}

    return results


def save_aggregated_report(results: Dict[str, Any], domain: str, out_dir: str = "reports") -> str:
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"ai_analysis_{domain}_{ts}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# AI Analysis Report for {domain}\n\n")
        for provider, res in results.items():
            f.write(f"## Provider: {provider}\n\n")
            if isinstance(res, dict) and "result" in res:
                f.write(res["result"] + "\n\n---\n\n")
            else:
                f.write("Error: " + json.dumps(res) + "\n\n")
    return out_path
