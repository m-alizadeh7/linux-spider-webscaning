"""
Base Provider Protocol and Classes
Defines the contract for all external API providers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class ProviderStatus(Enum):
    """Provider execution status"""
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    DISABLED = "disabled"
    MISSING_KEY = "missing_key"
    RATE_LIMITED = "rate_limited"


@dataclass
class ProviderResult:
    """Standard result from a provider"""
    provider_name: str
    status: ProviderStatus
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    
    def is_success(self) -> bool:
        """Check if provider execution was successful"""
        return self.status in (ProviderStatus.SUCCESS, ProviderStatus.PARTIAL)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'provider': self.provider_name,
            'status': self.status.value,
            'data': self.data,
            'errors': self.errors,
            'warnings': self.warnings,
            'execution_time': self.execution_time
        }


class Provider(ABC):
    """
    Abstract base class for external API providers
    
    All providers must implement:
    - name: Unique provider identifier
    - is_enabled(): Check if provider is configured and enabled
    - run(): Execute the provider logic
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this provider"""
        pass
    
    @property
    def description(self) -> str:
        """Human-readable description"""
        return f"{self.name} provider"
    
    @property
    def requires_api_key(self) -> bool:
        """Whether this provider requires an API key"""
        return True
    
    @property
    def is_heavy(self) -> bool:
        """Whether this provider requires heavy dependencies (e.g., Playwright)"""
        return False
    
    @abstractmethod
    def is_enabled(self, config: Dict[str, Any]) -> bool:
        """
        Check if this provider is enabled and properly configured
        
        Args:
            config: Configuration dictionary from providers config
            
        Returns:
            True if provider can be used
        """
        pass
    
    @abstractmethod
    def run(self, target: str, context: Dict[str, Any]) -> ProviderResult:
        """
        Execute the provider logic
        
        Args:
            target: Target URL or domain
            context: Additional context (e.g., existing scan results)
            
        Returns:
            ProviderResult with data or error information
        """
        pass
    
    def get_config_value(self, config: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Helper to get provider-specific config value"""
        provider_config = config.get('providers', {}).get(self.name, {})
        return provider_config.get(key, default)
    
    def get_api_key(self, config: Dict[str, Any]) -> Optional[str]:
        """Helper to get API key from config"""
        return self.get_config_value(config, 'api_key')
