"""
Provider Registry
Manages registration and discovery of providers
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Type
from .base import Provider, ProviderResult, ProviderStatus


class ProviderRegistry:
    """
    Central registry for all providers
    Handles provider registration, configuration, and execution
    """
    
    _instance: Optional['ProviderRegistry'] = None
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize registry
        
        Args:
            config_path: Path to providers configuration file
        """
        self._providers: Dict[str, Provider] = {}
        self._config: Dict[str, Any] = {}
        self._config_path = config_path or self._find_config_path()
        self._load_config()
    
    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> 'ProviderRegistry':
        """Get singleton instance of registry"""
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (useful for testing)"""
        cls._instance = None
    
    def _find_config_path(self) -> str:
        """Find providers config file"""
        base_path = Path(__file__).parent.parent.parent / 'config'
        
        # Try YAML first, then JSON
        yaml_path = base_path / 'providers.yaml'
        json_path = base_path / 'providers.json'
        
        if yaml_path.exists():
            return str(yaml_path)
        elif json_path.exists():
            return str(json_path)
        else:
            # Return YAML path as default (will be created)
            return str(yaml_path)
    
    def _load_config(self):
        """Load configuration from file"""
        if not os.path.exists(self._config_path):
            self._config = self._get_default_config()
            self._save_config()
            return
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                if self._config_path.endswith('.yaml') or self._config_path.endswith('.yml'):
                    self._config = yaml.safe_load(f) or {}
                else:
                    self._config = json.load(f)
        except Exception as e:
            print(f"[!] Failed to load providers config: {e}")
            self._config = self._get_default_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            config_dir = Path(self._config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self._config_path, 'w', encoding='utf-8') as f:
                if self._config_path.endswith('.yaml') or self._config_path.endswith('.yml'):
                    yaml.safe_dump(self._config, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"[!] Failed to save providers config: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'global': {
                'timeout': 30,
                'max_retries': 3,
                'enable_optional_providers': False
            },
            'providers': {
                # Example provider configurations (all disabled by default)
                'pagespeed': {
                    'enabled': False,
                    'api_key': '',
                    'timeout': 60
                },
                'playwright': {
                    'enabled': False,
                    'render_js': False,
                    'timeout': 30
                }
            }
        }
    
    def register(self, provider: Provider):
        """
        Register a provider
        
        Args:
            provider: Provider instance to register
        """
        self._providers[provider.name] = provider
    
    def unregister(self, provider_name: str):
        """
        Unregister a provider
        
        Args:
            provider_name: Name of provider to remove
        """
        if provider_name in self._providers:
            del self._providers[provider_name]
    
    def get_provider(self, name: str) -> Optional[Provider]:
        """
        Get a specific provider by name
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance or None
        """
        return self._providers.get(name)
    
    def get_all_providers(self) -> List[Provider]:
        """Get all registered providers"""
        return list(self._providers.values())
    
    def get_enabled_providers(self) -> List[Provider]:
        """
        Get all enabled and properly configured providers
        
        Returns:
            List of enabled providers
        """
        enabled = []
        for provider in self._providers.values():
            try:
                if provider.is_enabled(self._config):
                    # Skip heavy providers if dependencies not installed
                    if provider.is_heavy and not self._check_heavy_deps(provider):
                        continue
                    enabled.append(provider)
            except Exception as e:
                print(f"[!] Error checking provider {provider.name}: {e}")
        return enabled
    
    def _check_heavy_deps(self, provider: Provider) -> bool:
        """Check if heavy dependencies are available for a provider"""
        # This can be extended for specific dependency checks
        if provider.name == 'playwright':
            try:
                import playwright
                return True
            except ImportError:
                return False
        return True
    
    def run_providers(self, target: str, context: Dict[str, Any] = None, 
                     provider_names: List[str] = None) -> Dict[str, ProviderResult]:
        """
        Run enabled providers
        
        Args:
            target: Target URL
            context: Additional context
            provider_names: Specific providers to run (None = all enabled)
            
        Returns:
            Dictionary of provider name to result
        """
        context = context or {}
        results = {}
        
        if provider_names:
            providers = [self._providers[n] for n in provider_names if n in self._providers]
        else:
            providers = self.get_enabled_providers()
        
        for provider in providers:
            try:
                result = provider.run(target, context)
                results[provider.name] = result
            except Exception as e:
                results[provider.name] = ProviderResult(
                    provider_name=provider.name,
                    status=ProviderStatus.ERROR,
                    errors=[str(e)]
                )
        
        return results
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self._config.copy()
    
    def update_config(self, updates: Dict[str, Any]):
        """
        Update configuration
        
        Args:
            updates: Configuration updates to apply
        """
        self._config.update(updates)
        self._save_config()


# Convenience function
def get_registry(config_path: Optional[str] = None) -> ProviderRegistry:
    """Get the provider registry singleton"""
    return ProviderRegistry.get_instance(config_path)
