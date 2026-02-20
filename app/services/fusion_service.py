"""
Fusion Engine Service Module
Intelligently combines responses from multiple AI models
Enterprise-grade implementation with intelligent deduplication and synthesis
"""

import logging
import re
from typing import Dict, List, Any
from config import Config

logger = logging.getLogger(__name__)


class FusionService:
    """
    Fusion engine for combining responses from multiple AI providers
    - Removes duplicate information
    - Prioritizes accurate answers
    - Creates coherent, professional responses
    """
    
    def __init__(self):
        """Initialize fusion service with configuration"""
        self.enable_deduplication = Config.FUSION_ENABLE_DEDUPLICATION
        self.max_length = Config.FUSION_MAX_LENGTH
    
    def fuse_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Intelligently fuse responses from multiple AI providers
        
        Args:
            responses (List[Dict]): List of responses from different AI providers
        
        Returns:
            Dict with fused response and metadata
        """
        try:
            # Filter out error responses
            valid_responses = [r for r in responses if r.get('status') == 'success']
            
            if not valid_responses:
                return {
                    'status': 'error',
                    'message': 'No valid responses from AI providers',
                    'fused_response': 'Unable to process request at this time.'
                }
            
            # Extract response texts
            response_texts = [r.get('response', '') for r in valid_responses]
            providers = [r.get('provider', 'unknown') for r in valid_responses]
            
            # Fuse the responses
            fused_text = self._intelligent_fuse(response_texts, providers)
            
            # Apply length constraints
            fused_text = self._apply_length_limit(fused_text)
            
            return {
                'status': 'success',
                'fused_response': fused_text,
                'num_providers': len(valid_responses),
                'providers_used': providers,
                'confidence': self._calculate_confidence(valid_responses)
            }
        
        except Exception as e:
            logger.error(f"Error in fusion engine: {str(e)}", exc_info=True)
            return {
                'status': 'error',
                'message': f'Fusion error: {str(e)}',
                'fused_response': 'An error occurred while processing your request.'
            }
    
    def _intelligent_fuse(self, response_texts: List[str], providers: List[str]) -> str:
        """
        Intelligently combine responses by removing duplicates
        and creating coherent single response
        
        Args:
            response_texts (List[str]): Responses from different providers
            providers (List[str]): Provider names
        
        Returns:
            Fused response string
        """
        if len(response_texts) == 1:
            return response_texts[0]
        
        # Start with the longest response as base
        sorted_responses = sorted(zip(response_texts, providers), 
                                 key=lambda x: len(x[0]), 
                                 reverse=True)
        
        base_text = sorted_responses[0][0]
        
        # Remove duplicates and merge information
        if self.enable_deduplication:
            merged_text = self._merge_responses(base_text, sorted_responses[1:])
        else:
            merged_text = self._concatenate_responses(sorted_responses)
        
        return merged_text
    
    def _merge_responses(self, base_text: str, other_responses: List[tuple]) -> str:
        """
        Merge additional responses by extracting unique information
        
        Args:
            base_text (str): Base response text
            other_responses (List[tuple]): Other responses and providers
        
        Returns:
            Merged response
        """
        merged = base_text
        base_sentences = self._extract_sentences(base_text)
        
        for response_text, provider in other_responses:
            new_sentences = self._extract_sentences(response_text)
            
            # Find unique sentences not in base
            for sentence in new_sentences:
                if not self._is_duplicate_info(sentence, base_sentences):
                    # Add unique information from other providers
                    merged += f"\n\nAdditional insight from {provider.upper()}: {sentence}"
                    base_sentences.append(sentence)
        
        return merged
    
    def _concatenate_responses(self, sorted_responses: List[tuple]) -> str:
        """
        Simply concatenate responses when deduplication is disabled
        
        Args:
            sorted_responses (List[tuple]): Sorted responses and providers
        
        Returns:
            Concatenated response
        """
        sections = []
        provider_names = {
            'openai': 'ChatGPT',
            'gemini': 'Google Gemini',
            'deepseek': 'DeepSeek'
        }
        
        for response_text, provider in sorted_responses:
            provider_name = provider_names.get(provider, provider.upper())
            sections.append(f"**{provider_name}:**\n{response_text}")
        
        return "\n\n---\n\n".join(sections)
    
    def _extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text
        
        Args:
            text (str): Text to extract sentences from
        
        Returns:
            List of sentences
        """
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]
    
    def _is_duplicate_info(self, sentence: str, existing_sentences: List[str]) -> bool:
        """
        Check if sentence contains duplicate information
        
        Args:
            sentence (str): Sentence to check
            existing_sentences (List[str]): Existing sentences
        
        Returns:
            True if duplicate, False otherwise
        """
        # Simple similarity check
        sentence_lower = sentence.lower()
        sentence_words = set(sentence_lower.split())
        
        for existing in existing_sentences:
            existing_lower = existing.lower()
            existing_words = set(existing_lower.split())
            
            # If more than 60% overlap, consider it duplicate
            overlap = len(sentence_words & existing_words)
            total_words = len(sentence_words | existing_words)
            
            if total_words > 0 and overlap / total_words > 0.6:
                return True
        
        return False
    
    def _apply_length_limit(self, text: str, max_length: int = None) -> str:
        """
        Apply maximum length constraint
        
        Args:
            text (str): Text to constrain
            max_length (int): Maximum length
        
        Returns:
            Constrained text
        """
        if max_length is None:
            max_length = self.max_length
        
        if len(text) <= max_length:
            return text
        
        # Truncate to max length while preserving complete sentences
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.8:  # If period is in last 20%
            return truncated[:last_period + 1]
        
        return truncated.rsplit(' ', 1)[0] + '...'
    
    def _calculate_confidence(self, valid_responses: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence score based on number of providers
        and response consistency
        
        Args:
            valid_responses (List[Dict]): Valid responses from providers
        
        Returns:
            Confidence score (0-1)
        """
        num_providers = len(valid_responses)
        
        # Base confidence on number of providers
        base_confidence = min(num_providers / 3, 1.0)
        
        return round(base_confidence, 2)


# Singleton instance
fusion_service = FusionService()
