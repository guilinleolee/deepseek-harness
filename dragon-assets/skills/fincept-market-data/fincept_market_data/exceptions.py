"""
Fincept Market Data Exceptions
自定义异常类
"""


class FinceptError(Exception):
    """Base exception for fincept-market-data"""
    pass


class RateLimitError(FinceptError):
    """Rate limit exceeded, retry later"""
    pass


class DataNotFoundError(FinceptError):
    """Data not found for the given symbol or parameters"""
    pass


class ProviderError(FinceptError):
    """Generic provider error"""
    pass


class AuthenticationError(FinceptError):
    """Authentication failed (invalid API key)"""
    pass


class ValidationError(FinceptError):
    """Input validation error"""
    pass


class CacheError(FinceptError):
    """Cache operation error"""
    pass
