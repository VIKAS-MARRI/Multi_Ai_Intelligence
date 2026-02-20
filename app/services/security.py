"""
Security Utilities Module
Provides functions for secure handling of API keys and sensitive data
"""

import os
import re
import logging
import secrets
import string
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for safe logging, showing only last N characters.
    
    Args:
        api_key: The API key to mask
        visible_chars: Number of characters to show at the end
        
    Returns:
        Masked API key string
    """
    if not api_key or len(api_key) <= visible_chars:
        return "***REDACTED***"
    return "***" + api_key[-visible_chars:]


def validate_api_key(api_key: str, provider: str) -> bool:
    """
    Validate API key format for each provider.
    
    Args:
        api_key: The API key to validate
        provider: Provider name (openai, gemini, deepseek)
        
    Returns:
        True if key appears valid, False otherwise
    """
    if not api_key or api_key.startswith("your-"):
        return False
    
    # Provider-specific validation patterns
    patterns = {
        'openai': r'^sk-[A-Za-z0-9\-]+$',
        'gemini': r'^[A-Za-z0-9_\-]{20,}$',
        'deepseek': r'^sk-[A-Za-z0-9\-]+$',
    }
    
    pattern = patterns.get(provider.lower())
    if pattern and re.match(pattern, api_key):
        return True
    return len(api_key) > 10  # Basic fallback check


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key.
    
    Args:
        length: Length of the key to generate
        
    Returns:
        Random secret key string
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class SensitiveDataFilter(logging.Filter):
    """
    Logging filter to mask sensitive information in logs.
    """
    
    # Patterns to match sensitive data
    SENSITIVE_PATTERNS = [
        r'(api[_-]?key)["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_]{10,})["\']?',
        r'(bearer|authorization)["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_]{10,})["\']?',
        r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\']+)["\']?',
        r'(secret|token)["\']?\s*[:=]\s*["\']?([A-Za-z0-9\-_]{10,})["\']?',
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records to mask sensitive data"""
        record.msg = self._mask_sensitive_data(str(record.msg))
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._mask_sensitive_data(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self._mask_sensitive_data(str(arg)) for arg in record.args)
        return True
    
    @staticmethod
    def _mask_sensitive_data(text: str) -> str:
        """Mask sensitive data in text"""
        for pattern in SensitiveDataFilter.SENSITIVE_PATTERNS:
            text = re.sub(pattern, r'\1=***REDACTED***', text, flags=re.IGNORECASE)
        return text


def validate_environment_security() -> Dict[str, any]:
    """
    Validate security configuration of the environment.
    
    Returns:
        Dictionary with validation results and warnings
    """
    issues = []
    warnings = []
    
    # Check SECRET_KEY
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or secret_key == 'dev-secret-key-NOT-FOR-PRODUCTION':
        if os.getenv('FLASK_ENV') == 'production':
            issues.append("SECRET_KEY not properly set for production")
        else:
            warnings.append("Using development SECRET_KEY")
    elif len(secret_key) < 32:
        warnings.append("SECRET_KEY should be at least 32 characters")
    
    # Check API keys are not placeholder values
    api_keys = {
        'OPENAI_API_KEY': 'openai',
        'GEMINI_API_KEY': 'gemini',
        'DEEPSEEK_API_KEY': 'deepseek',
    }
    
    for env_var, provider in api_keys.items():
        key = os.getenv(env_var)
        if key and key.startswith('your-'):
            warnings.append(f"{env_var} not configured (using placeholder)")
        elif key and not validate_api_key(key, provider):
            warnings.append(f"{env_var} may be invalid format")
    
    # Check debug mode in production
    if os.getenv('FLASK_ENV') == 'production' and os.getenv('FLASK_DEBUG', '').lower() == 'true':
        issues.append("DEBUG mode should be disabled in production")
    
    # Check session security in production
    if os.getenv('FLASK_ENV') == 'production' and os.getenv('SESSION_COOKIE_SECURE', '').lower() != 'true':
        issues.append("SESSION_COOKIE_SECURE should be True in production")
    
    return {
        'issues': issues,
        'warnings': warnings,
        'secure': len(issues) == 0,
    }


def print_security_status() -> None:
    """Print security validation status"""
    result = validate_environment_security()
    
    if result['issues']:
        print("\n⚠️  SECURITY ISSUES FOUND:")
        for issue in result['issues']:
            print(f"  ❌ {issue}")
    
    if result['warnings']:
        print("\n⚠️  SECURITY WARNINGS:")
        for warning in result['warnings']:
            print(f"  ⚠️  {warning}")
    
    if result['secure']:
        print("\n✅ Security validation passed")
