"""
Main Routes Module
Handles main application routes
"""

from flask import Blueprint, render_template, jsonify, request, current_app
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Serve the main dashboard page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return {'error': 'Failed to load dashboard'}, 500


@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'Jarvis Multi-AI Voice Assistant'
    }), 200


@main_bp.route('/api/config')
def get_config():
    """Get client-side configuration"""
    return jsonify({
        'voice_engine': current_app.config.get('VOICE_ENGINE'),
        'api_timeout': current_app.config.get('API_TIMEOUT'),
        'fusion_enabled': True
    }), 200
