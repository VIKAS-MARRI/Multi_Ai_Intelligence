"""
Google Gemini Service Module
Handles integration with Google Gemini API
Enterprise-grade implementation with error handling and logging
"""

import asyncio
import logging
from typing import Dict, Any
from config import Config

logger = logging.getLogger(__name__)

# Import Gemini API - suppress deprecation warning
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    try:
        import google.generativeai as genai
    except ImportError:
        logger.warning("Google Generative AI package not available")
        genai = None


class GeminiService:
    """
    Service for interacting with Google Gemini API
    Provides methods for querying Gemini models
    """
    
    def __init__(self):
        """Initialize Gemini service with API key from config"""
        self.api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.timeout = Config.GEMINI_TIMEOUT
        self.model = None
        
        if not self.api_key:
            logger.warning("Gemini API key not configured")
        elif genai is None:
            logger.warning("Google Generative AI package not installed")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.error(f"Error initializing Gemini service: {e}")
    
    async def query(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Query Gemini API asynchronously
        
        Args:
            prompt (str): The user's input prompt
            max_tokens (int): Maximum tokens in response
        
        Returns:
            Dict with response data or error information
        """
        try:
            if not self.api_key or self.model is None:
                return {
                    'status': 'error',
                    'message': 'Gemini not configured' if self.model is None else 'Gemini API key not configured',
                    'provider': 'gemini'
                }
            
            # Run the Gemini API call in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, self._make_request, prompt, max_tokens),
                timeout=self.timeout
            )
            
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Gemini API timeout after {self.timeout}s")
            return {
                'status': 'error',
                'message': 'Gemini API timeout',
                'provider': 'gemini'
            }
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'Gemini API error: {str(e)}',
                'provider': 'gemini'
            }
    
    def _make_request(self, prompt: str, max_tokens: int) -> Dict[str, Any]:
        """
        Make synchronous request to Gemini API
        
        Args:
            prompt (str): The user's input prompt
            max_tokens (int): Maximum tokens in response
        
        Returns:
            Dict with response data
        """
        try:
            generation_config = {
                "max_output_tokens": max_tokens,
                "temperature": 0.7,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                stream=False
            )
            
            return {
                'status': 'success',
                'provider': 'gemini',
                'model': self.model_name,
                'response': response.text,
            }
        
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return {
                'status': 'error',
                'message': f'Gemini API error: {str(e)}',
                'provider': 'gemini'
            }


# Singleton instance
try:
    gemini_service = GeminiService()
except Exception as e:
    logger.error(f"Failed to create Gemini service: {e}")
    gemini_service = GeminiService() if genai else None
