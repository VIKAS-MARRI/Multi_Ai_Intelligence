"""
Provider Manager
Handles model discovery, provider health checks, intelligent routing and structured provider logging.
"""
import os
import time
import json
import logging
from typing import Dict, Any, List
import requests

from config import Config
from app.services import openai_service, deepseek_service, gemini_service

logger = logging.getLogger('providers')


def _ensure_log_handler():
    """Ensure file handler is attached for provider logs."""
    log_dir = getattr(Config, 'LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    fh = None
    for h in logger.handlers:
        if getattr(h, 'name', '') == 'provider_file':
            fh = h
            break
    if not fh:
        fh = logging.FileHandler(os.path.join(log_dir, 'provider.log'), encoding='utf-8')
        fh.setLevel(logging.INFO)
        fh.name = 'provider_file'
        formatter = logging.Formatter('%(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)


def _log_provider_event(provider: str, model: str, status: str, latency: float, error: str = ''):
    _ensure_log_handler()
    entry = {
        'timestamp': time.time(),
        'provider': provider,
        'model': model,
        'status': status,
        'latency': round(latency, 3),
        'error': error
    }
    logger.info(json.dumps(entry, ensure_ascii=False))


def validate_env() -> Dict[str, str]:
    """Check required env vars exist (without printing keys)."""
    statuses = {}
    providers = [
        ('OpenAI', 'OPENAI_API_KEY'),
        ('DeepSeek', 'DEEPSEEK_API_KEY'),
        ('Gemini', 'GEMINI_API_KEY')
    ]
    for name, var in providers:
        statuses[name] = 'configured' if bool(os.getenv(var)) else 'missing'
    # Models
    models = {}
    models['OPENAI_MODEL'] = os.getenv('OPENAI_MODEL') or Config.OPENAI_MODEL
    models['DEEPSEEK_MODEL'] = os.getenv('DEEPSEEK_MODEL') or Config.DEEPSEEK_MODEL
    models['GEMINI_MODEL'] = os.getenv('GEMINI_MODEL') or Config.GEMINI_MODEL
    return {'providers': statuses, 'models': models}


def discover_openai_model() -> str:
    """Attempt to discover best OpenAI chat model. Returns model name or existing config."""
    try:
        import openai
        start = time.time()
        # Try Model.list if available
        models = None
        if hasattr(openai, 'Model') and hasattr(openai.Model, 'list'):
            resp = openai.Model.list()
            models = [m.id for m in getattr(resp, 'data', resp)]
        elif hasattr(openai, 'Engine') and hasattr(openai.Engine, 'list'):
            resp = openai.Engine.list()
            models = [m.id for m in getattr(resp, 'data', resp)]
        # Choose a model heuristic: prefer 'gpt-4' family then 'gpt-3.5'
        chosen = None
        if models:
            for candidate in ['gpt-4', 'gpt-4o', 'gpt-3.5-turbo', 'gpt-4o-mini', 'gpt-3.5']:
                for m in models:
                    if candidate in m:
                        chosen = m
                        break
                if chosen:
                    break
        latency = time.time() - start
        model = chosen or Config.OPENAI_MODEL
        Config.OPENAI_MODEL = model
        _log_provider_event('openai', model, 'discovered', latency)
        return model
    except Exception as e:
        _log_provider_event('openai', Config.OPENAI_MODEL, 'discover_failed', 0.0, str(e))
        return Config.OPENAI_MODEL


def discover_deepseek_model() -> str:
    """Attempt to discover DeepSeek models using its base URL or OpenAI compatibility."""
    start = time.time()
    base = Config.DEEPSEEK_BASE_URL.rstrip('/')
    try:
        # Try DeepSeek's /models endpoint
        r = requests.get(f"{base}/models", headers={
            'Authorization': f"Bearer {os.getenv('DEEPSEEK_API_KEY','')}",
            'Accept': 'application/json'
        }, timeout=5)
        if r.status_code == 200:
            data = r.json()
            # Expecting data.models or data['models']
            models = data.get('models') if isinstance(data, dict) else None
            if not models and isinstance(data, list):
                models = data
            chosen = None
            if models:
                for m in models:
                    mid = m.get('id') if isinstance(m, dict) else m
                    if 'deepseek' in str(mid).lower() or 'chat' in str(mid).lower():
                        chosen = mid
                        break
            model = chosen or Config.DEEPSEEK_MODEL
            latency = time.time() - start
            Config.DEEPSEEK_MODEL = model
            _log_provider_event('deepseek', model, 'discovered', latency)
            return model
    except Exception as e:
        _log_provider_event('deepseek', Config.DEEPSEEK_MODEL, 'discover_failed', 0.0, str(e))
    # Fallback: return configured
    return Config.DEEPSEEK_MODEL


def discover_gemini_model() -> str:
    """Attempt to discover a valid Gemini generateContent model."""
    start = time.time()
    try:
        # Try google.generativeai or google.genai patterns
        try:
            import google.generativeai as genai
            if hasattr(genai, 'list_models'):
                models = genai.list_models()
                ids = [m['name'] for m in models]
            else:
                ids = []
        except Exception:
            try:
                import google.genai as gen
                # newer clients may have get_models()
                if hasattr(gen, 'Models') and hasattr(gen.Models, 'list'):
                    resp = gen.Models.list()
                    ids = [m.name for m in getattr(resp, 'models', [])]
                else:
                    ids = []
            except Exception:
                ids = []

        chosen = None
        for candidate in ['gemini', 'gemini-pro', 'gemini-1', 'gemini-1.5']:
            for m in ids:
                if candidate in m:
                    chosen = m
                    break
            if chosen:
                break

        model = chosen or Config.GEMINI_MODEL
        latency = time.time() - start
        Config.GEMINI_MODEL = model
        _log_provider_event('gemini', model, 'discovered', latency)
        return model
    except Exception as e:
        _log_provider_event('gemini', Config.GEMINI_MODEL, 'discover_failed', 0.0, str(e))
        return Config.GEMINI_MODEL


def test_provider_call(provider_name: str, prompt: str = 'Reply with: PROVIDER_OK') -> Dict[str, Any]:
    """Send a small test prompt to a single provider and return status and latency."""
    start = time.time()
    try:
        if provider_name == 'openai':
            res = openai_service.query(prompt, max_tokens=32)
            # openai_service.query is async; if returned coroutine, run it
            import asyncio
            if hasattr(res, '__await__'):
                res = asyncio.run(res)
            latency = time.time() - start
            status = 'ok' if res.get('status') == 'success' else 'failed'
            _log_provider_event('openai', Config.OPENAI_MODEL, status, latency, res.get('message',''))
            return {'provider': 'openai', 'status': status, 'detail': res}

        if provider_name == 'deepseek':
            res = deepseek_service.query(prompt, max_tokens=32)
            import asyncio
            if hasattr(res, '__await__'):
                res = asyncio.run(res)
            latency = time.time() - start
            status = 'ok' if res.get('status') == 'success' else 'failed'
            _log_provider_event('deepseek', Config.DEEPSEEK_MODEL, status, latency, res.get('message',''))
            return {'provider': 'deepseek', 'status': status, 'detail': res}

        if provider_name == 'gemini':
            res = gemini_service.query(prompt, max_tokens=32)
            import asyncio
            if hasattr(res, '__await__'):
                res = asyncio.run(res)
            latency = time.time() - start
            status = 'ok' if res.get('status') == 'success' else 'failed'
            _log_provider_event('gemini', Config.GEMINI_MODEL, status, latency, res.get('message',''))
            return {'provider': 'gemini', 'status': status, 'detail': res}

    except Exception as e:
        latency = time.time() - start
        _log_provider_event(provider_name, getattr(Config, f"{provider_name.upper()}_MODEL", ''), 'failed', latency, str(e))
        return {'provider': provider_name, 'status': 'failed', 'detail': {'message': str(e)}}


def query_with_fallback(prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
    """Query providers in priority order with automatic fallback.
    Priority: Gemini -> OpenAI -> DeepSeek -> Local fallback
    Returns a structured result with provider, model, response, and latency.
    """
    def _local_fallback(prompt_text: str) -> Dict[str, Any]:
        # Always-available minimal fallback to keep the system operational.
        return {
            'status': 'success',
            'provider': 'fallback',
            'model': 'local-fallback',
            'response': 'Jarvis is active. External AI providers are unavailable, but core system is operational.',
            'latency': 0.0,
            'raw': {'message': 'local fallback'}
        }

    order = [('gemini', gemini_service, Config.GEMINI_MODEL),
             ('openai', openai_service, Config.OPENAI_MODEL),
             ('deepseek', deepseek_service, Config.DEEPSEEK_MODEL)]

    for name, service, model in order:
        try:
            start = time.time()
            if service is None:
                continue
            res = service.query(prompt, max_tokens)
            import asyncio
            if hasattr(res, '__await__'):
                res = asyncio.run(res)
            latency = time.time() - start
            if res.get('status') == 'success':
                _log_provider_event(name, model, 'success', latency)
                return {
                    'status': 'success',
                    'provider': name,
                    'model': model,
                    'response': res.get('response'),
                    'latency': round(latency, 3),
                    'raw': res
                }
            else:
                _log_provider_event(name, model, 'failed', latency, res.get('message',''))
        except Exception as e:
            latency = time.time() - start
            _log_provider_event(name, model, 'failed', latency, str(e))
            continue

    # If none of the external providers succeeded, return local fallback
    fb = _local_fallback(prompt)
    _log_provider_event('fallback', fb.get('model'), 'success', fb.get('latency', 0.0))
    return fb
