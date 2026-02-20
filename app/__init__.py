"""
Multi-AI Voice Assistant Application
Flask application factory
"""

import os
import logging
from flask import Flask
from config import get_config

# Get the absolute path to the app directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app(config_class=None):
    """
    Application factory to create and configure the Flask app
    
    Args:
        config_class: Configuration class to use (defaults to environment-based config)
    
    Returns:
        Flask application instance
    """
    
    if config_class is None:
        config_class = get_config()
    
    app = Flask(__name__, 
                static_folder=os.path.join(APP_DIR, 'static'),
                template_folder=os.path.join(APP_DIR, 'templates'))
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # CORS configuration
    setup_cors(app)
    
    return app


def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes.main_routes import main_bp
    from app.routes.ai_routes import ai_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(ai_bp, url_prefix='/api')


def setup_logging(app):
    """Setup application logging"""
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_dir = app.config.get('LOG_DIR', 'logs')
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def setup_error_handlers(app):
    """Setup error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'detail': str(error)}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal server error: {error}')
        return {'error': 'Internal Server Error'}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad Request', 'detail': str(error)}, 400


def setup_cors(app):
    """Setup CORS configuration"""
    # For production, configure specific origins
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
