"""
OpenAI Service Module
Handles integration with OpenAI API (ChatGPT)
Enterprise-grade implementation with error handling and logging
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any
from config import Config

# Try to import the modern OpenAI client if available
try:
    from openai import OpenAI as OpenAIClient
    _HAS_NEW_OPENAI = True
except Exception:
    OpenAIClient = None
    _HAS_NEW_OPENAI = False
    import openai

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service for interacting with OpenAI API
    Provides methods for querying ChatGPT models
    """
    
    def __init__(self):
        """Initialize OpenAI service with API key from config"""
        self.api_key = Config.OPENAI_API_KEY
        self.model = Config.OPENAI_MODEL
        self.timeout = Config.OPENAI_TIMEOUT
        self._client = None
        self._init_client()
        
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
        else:
            try:
                if _HAS_NEW_OPENAI and OpenAIClient is not None:
                    self._client = OpenAIClient(api_key=self.api_key)
                else:
                    openai.api_key = self.api_key
            except Exception:
                openai.api_key = self.api_key

    def _init_client(self):
        if _HAS_NEW_OPENAI and OpenAIClient is not None and self.api_key:
            try:
                self._client = OpenAIClient(api_key=self.api_key)
            except Exception:
                self._client = None
    
    async def query(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Query OpenAI API asynchronously
        
        Args:
            prompt (str): The user's input prompt
            max_tokens (int): Maximum tokens in response
        
        Returns:
            Dict with response data or error information
        """
        try:
            if not self.api_key:
                return {
                    'status': 'error',
                    'message': 'OpenAI API key not configured',
                    'provider': 'openai'
                }
            
            # Run the OpenAI API call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self._make_request, prompt, max_tokens)
            
            return response
            
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}", exc_info=True)
            return {'status': 'error', 'message': f'OpenAI API error: {str(e)}', 'provider': 'openai'}
    
    def _make_request(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """
        Make synchronous request to OpenAI API
        
        Args:
            prompt (str): The user's input prompt
            max_tokens (int): Maximum tokens in response
        
        Returns:
            Dict with response data
        """
        # Implement simple retry logic with exponential backoff
        last_exc = None
        for attempt in range(3):
            try:
                if self._client is not None:
                    # Modern OpenAI client
                    response = self._client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are Jarvis, an intelligent AI assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=0.7,
                        timeout=self.timeout
                    )
                    # New client returns response-like object; coerce to dict
                    text = None
                    tokens_used = None
                    if isinstance(response, dict):
                        text = response.get('choices', [{}])[0].get('message', {}).get('content')
                        usage = response.get('usage', {})
                        tokens_used = usage.get('total_tokens')
                    else:
                        # try attribute access
                        try:
                            text = response.choices[0].message.content
                        except Exception:
                            text = str(response)

                    return {'status': 'success', 'provider': 'openai', 'model': self.model, 'response': text, 'tokens_used': tokens_used}
                else:
                    # Fallback to older openai SDK
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are Jarvis, an intelligent AI assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=max_tokens,
                        temperature=0.7,
                        timeout=self.timeout
                    )
                    return {
                        'status': 'success',
                        'provider': 'openai',
                        'model': self.model,
                        'response': response['choices'][0]['message']['content'],
                        'tokens_used': response['usage']['total_tokens']
                    }
            except Exception as e:
                last_exc = e
                logger.warning(f"OpenAI request attempt {attempt+1} failed: {e}")
                time.sleep(0.5 * (2 ** attempt))

        logger.error(f"OpenAI API error after retries: {last_exc}")
        return {'status': 'error', 'message': f'OpenAI API error: {str(last_exc)}', 'provider': 'openai'}


# Singleton instance
openai_service = OpenAIService()
