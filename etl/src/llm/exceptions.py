# etl/src/llm/exceptions.py
class LLMAPIError(Exception):
    """Базовое исключение для ошибок LLM API."""
    pass

class RateLimitError(LLMAPIError):
    """Исключение для превышения лимита запросов."""
    pass

class AuthenticationError(LLMAPIError):
    """Исключение для ошибок аутентификации."""
    pass

class BadResponseError(LLMAPIError):
    """Исключение для некорректного ответа от LLM."""
    pass