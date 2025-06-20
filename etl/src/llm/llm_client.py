# etl/src/llm/llm_client.py
import os
from typing import Optional, Dict, Any
import openai
from .exceptions import LLMAPIError, AuthenticationError

class LLMClient:
    def __init__(self, provider: str, api_key: str, model_name: str, api_endpoint: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name
        self.api_endpoint = api_endpoint

        if not self.api_key:
            raise ValueError("LLM API key is required.")

        if self.provider == 'openai':
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            raise NotImplementedError(f"Provider '{self.provider}' is not supported.")

    async def send_request_to_llm(self, prompt: str, **kwargs) -> str:
        """Отправляет запрос к LLM и возвращает текстовый ответ."""
        try:
            if self.provider == 'openai':
                return await self._call_openai_api(prompt, **kwargs)
            # В будущем здесь можно добавить других провайдеров
            # elif self.provider == 'gemini':
            #     return await self._call_gemini_api(prompt, **kwargs)
            else:
                 raise NotImplementedError(f"Provider '{self.provider}' is not supported.")
        except openai.AuthenticationError as e:
            raise AuthenticationError(f"OpenAI Authentication Error: {e}") from e
        except Exception as e:
            raise LLMAPIError(f"An unexpected error occurred with LLM provider '{self.provider}': {e}") from e

    async def _call_openai_api(self, prompt: str, **kwargs) -> str:
        """Приватный метод для вызова OpenAI API."""
        completion = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for data extraction."},
                {"role": "user", "content": prompt}
            ],
            temperature=kwargs.get('temperature', 0.1),
            max_tokens=kwargs.get('max_tokens', 4096),
        )
        response = completion.choices[0].message.content
        if not response:
            raise LLMAPIError("Received an empty response from OpenAI.")
        return response