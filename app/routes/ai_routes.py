"""
AI Routes Module
Handles all AI model queries and fusion
"""

from flask import Blueprint, request, jsonify, current_app
import asyncio
import logging
from typing import Dict, Any, List
import json

from app.services.openai_service import openai_service
from app.services.gemini_service import gemini_service
from app.services.deepseek_service import deepseek_service
from app.services.fusion_service import fusion_service
from app.services.voice_service import voice_service
from app.services.provider_manager import (
    validate_env,
    discover_openai_model,
    discover_deepseek_model,
    discover_gemini_model,
    test_provider_call,
    query_with_fallback
)

logger = logging.getLogger(__name__)

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/query', methods=['POST'])
def query():
    """
    Main endpoint to query all AI providers and fuse results
    
    Request JSON:
    {
        "prompt": "User's question",
        "max_tokens": 1000,
        "enable_fusion": true
    }
    
    Response JSON:
    {
        "status": "success",
        "query": "User's question",
        "responses": {
            "openai": {...},
            "gemini": {...},
            "deepseek": {...}
        },
        "fused_response": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: prompt'
            }), 400
        
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({
                'status': 'error',
                'message': 'Prompt cannot be empty'
            }), 400
        
        # Validate prompt length
        if len(prompt) > 5000:
            return jsonify({
                'status': 'error',
                'message': 'Prompt is too long (max 5000 characters)'
            }), 400
        
        max_tokens = data.get('max_tokens', 1000)
        enable_fusion = data.get('enable_fusion', True)
        
        logger.info(f"Processing query: {prompt[:100]}...")
        
        # Use intelligent routing with fallback to get one best provider response
        single_result = query_with_fallback(prompt, max_tokens)

        # Also keep the original parallel provider responses for visibility
        responses = asyncio.run(query_all_providers(prompt, max_tokens))

        # Save provider responses for debugging (no keys)
        try:
            debug_path = 'last_query_responses.json'
            with open(debug_path, 'w', encoding='utf-8') as f:
                json.dump(responses, f, indent=2, ensure_ascii=False)
        except Exception:
            logger.exception('Failed to write provider responses debug file')
        
        result = {
            'status': 'success',
            'query': prompt,
            'responses': responses,
            'selected': single_result,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        # Apply fusion if enabled
        if enable_fusion:
            fused = fusion_service.fuse_responses(
                list(responses.values())
            )
            result['fused_response'] = fused
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in query endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Error processing query: {str(e)}'
        }), 500


async def query_all_providers(prompt: str, max_tokens: int) -> Dict[str, Any]:
    """
    Query all AI providers concurrently
    
    Args:
        prompt (str): User prompt
        max_tokens (int): Maximum tokens
    
    Returns:
        Dict with responses from all providers
    """
    # Create tasks for all providers
    tasks = [
        openai_service.query(prompt, max_tokens),
        gemini_service.query(prompt, max_tokens),
        deepseek_service.query(prompt, max_tokens)
    ]
    
    # Execute all queries concurrently
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"Error gathering results: {str(e)}")
        results = []
    
    # Organize results
    responses = {
        'openai': results[0] if len(results) > 0 else {'status': 'error'},
        'gemini': results[1] if len(results) > 1 else {'status': 'error'},
        'deepseek': results[2] if len(results) > 2 else {'status': 'error'}
    }
    
    return responses


@ai_bp.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    """
    Convert speech to text from audio data
    
    Request: Form data with 'audio' file
    Response: Dict with transcribed text
    """
    try:
        if 'audio' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        logger.info(f"Processing audio file: {audio_file.filename}")
        
        result = asyncio.run(voice_service.speech_to_text(audio_data))
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
    
    except Exception as e:
        logger.error(f"Error in speech_to_text: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Error processing audio: {str(e)}'
        }), 500


@ai_bp.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech
    
    Request JSON:
    {
        "text": "Text to speak"
    }
    
    Response: Dict with audio URL
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: text'
            }), 400
        
        text = data.get('text', '').strip()
        if not text:
            return jsonify({
                'status': 'error',
                'message': 'Text cannot be empty'
            }), 400
        
        logger.info(f"Converting text to speech: {text[:50]}...")
        
        result = asyncio.run(voice_service.text_to_speech(text))
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
    
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Error generating speech: {str(e)}'
        }), 500


@ai_bp.route('/fusion-only', methods=['POST'])
def fusion_only():
    """
    Fuse pre-existing responses without querying providers
    
    Request JSON:
    {
        "responses": [
            {"status": "success", "response": "...", "provider": "openai"},
            ...
        ]
    }
    
    Response: Dict with fused response
    """
    try:
        data = request.get_json()
        
        if not data or 'responses' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: responses'
            }), 400
        
        responses = data.get('responses', [])
        
        if not isinstance(responses, list) or len(responses) == 0:
            return jsonify({
                'status': 'error',
                'message': 'Responses must be a non-empty list'
            }), 400
        
        fused = fusion_service.fuse_responses(responses)
        
        return jsonify(fused), 200
    
    except Exception as e:
        logger.error(f"Error in fusion_only: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Error in fusion: {str(e)}'
        }), 500


@ai_bp.route('/providers', methods=['GET'])
def get_providers():
    """Get list of available AI providers and their status"""
    return jsonify({
        'providers': [
            {
                'name': 'openai',
                'display_name': 'ChatGPT',
                'configured': bool(__import__('os').getenv('OPENAI_API_KEY')),
            },
            {
                'name': 'gemini',
                'display_name': 'Google Gemini',
                'configured': bool(__import__('os').getenv('GEMINI_API_KEY')),
            },
            {
                'name': 'deepseek',
                'display_name': 'DeepSeek',
                'configured': bool(__import__('os').getenv('DEEPSEEK_API_KEY')),
            }
        ]
    }), 200



@ai_bp.route('/test-e2e', methods=['GET'])
def test_e2e():
    """Test endpoint that runs an end-to-end mock flow for local testing.

    Produces stubbed provider responses, runs fusion, performs TTS,
    and returns combined result so you can validate the full pipeline
    without external API keys.
    """
    try:
        prompt = request.args.get('prompt', 'Hello from E2E test')

        # Create stub provider responses
        stub_openai = {'status': 'success', 'provider': 'openai', 'response': f'OpenAI mock reply for: {prompt}'}
        stub_gemini = {'status': 'success', 'provider': 'gemini', 'response': f'Gemini mock reply for: {prompt}'}
        stub_deepseek = {'status': 'success', 'provider': 'deepseek', 'response': f'DeepSeek mock reply for: {prompt}'}

        responses = {
            'openai': stub_openai,
            'gemini': stub_gemini,
            'deepseek': stub_deepseek
        }

        # Run fusion on stubbed responses
        fused = fusion_service.fuse_responses(list(responses.values()))

        # Attempt TTS of fused response (if fusion succeeded)
        tts_result = {'status': 'skipped'}
        if fused and fused.get('status') == 'success':
            tts_result = asyncio.run(voice_service.text_to_speech(fused.get('fused_response', '')))

        result = {
            'status': 'success',
            'prompt': prompt,
            'responses': responses,
            'fused_response': fused,
            'tts': tts_result
        }

        # Write debug file
        try:
            with open('test_e2e_result.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        except Exception:
            logger.exception('Failed to write test_e2e_result.json')

        return jsonify(result), 200

    except Exception as e:
        logger.error('Error in test_e2e: %s', str(e), exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500
