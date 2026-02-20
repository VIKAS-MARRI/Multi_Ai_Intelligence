"""
DeepSeek Service Module
Handles integration with DeepSeek API
Enterprise-grade implementation with error handling and logging
"""

import asyncio
import logging
import time
from typing import Dict, Any
from config import Config

# Try to import modern OpenAI client for DeepSeek compatibility
try:
    from openai import OpenAI as OpenAIClient
    _HAS_NEW_OPENAI = True
except Exception:
    OpenAIClient = None
    _HAS_NEW_OPENAI = False
    import openai

logger = logging.getLogger(__name__)


class DeepSeekService:
    """
    Service for interacting with DeepSeek API
    Uses OpenAI-compatible API format
    """
    
    def __init__(self):
        """Initialize DeepSeek service with API key from config"""
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = Config.DEEPSEEK_BASE_URL
        self.model = Config.DEEPSEEK_MODEL
        self.timeout = Config.DEEPSEEK_TIMEOUT
        
        if not self.api_key:
            logger.warning("DeepSeek API key not configured")
        
        # Configure OpenAI client for DeepSeek (either new client or legacy)
        self._client = None
        try:
            if _HAS_NEW_OPENAI and OpenAIClient is not None:
                self._client = OpenAIClient(api_key=self.api_key)
            else:
                openai.api_key = self.api_key
                openai.api_base = self.base_url
        except Exception:
            openai.api_key = self.api_key
            openai.api_base = self.base_url
    
    async def query(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Query DeepSeek API asynchronously
        
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
                    'message': 'DeepSeek API key not configured',
                    'provider': 'deepseek'
                }
            
            # Run the DeepSeek API call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, self._make_request, prompt, max_tokens),
                timeout=self.timeout
            )
            
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"DeepSeek API timeout after {self.timeout}s")
            return {
                'status': 'error',
                'message': 'DeepSeek API timeout',
                'provider': 'deepseek'
            }
        except Exception as e:
            logger.error(f"DeepSeek error: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'DeepSeek API error: {str(e)}',
                'provider': 'deepseek'
            }
    
    def _make_request(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """
        Make synchronous request to DeepSeek API
        
        Args:
            prompt (str): The user's input prompt
            max_tokens (int): Maximum tokens in response
        
        Returns:
            Dict with response data
        """
        last_exc = None
        for attempt in range(3):
            try:
                if self._client is not None:
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
                    try:
                        text = response.choices[0].message.content
                    except Exception:
                        text = str(response)
                    return {'status': 'success', 'provider': 'deepseek', 'model': self.model, 'response': text}
                else:
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
                    return {'status': 'success', 'provider': 'deepseek', 'model': self.model, 'response': response['choices'][0]['message']['content'], 'tokens_used': response['usage']['total_tokens']}
            except Exception as e:
                last_exc = e
                logger.warning(f"DeepSeek request attempt {attempt+1} failed: {e}")
                time.sleep(0.5 * (2 ** attempt))

        logger.error(f"DeepSeek API error after retries: {last_exc}")
        return {'status': 'error', 'message': f'DeepSeek API error: {str(last_exc)}', 'provider': 'deepseek'}


# Singleton instance
deepseek_service = DeepSeekService()
