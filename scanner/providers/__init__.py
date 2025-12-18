"""
Provider/Plugin System for External API Integrations
All providers are optional and work as drop-in plugins
"""

from .base import Provider, ProviderResult
from .registry import ProviderRegistry, get_registry

__all__ = ['Provider', 'ProviderResult', 'ProviderRegistry', 'get_registry']
