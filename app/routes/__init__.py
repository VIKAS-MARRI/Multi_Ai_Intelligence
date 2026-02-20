"""
Routes Module
Exports all blueprints
"""

from app.routes.main_routes import main_bp
from app.routes.ai_routes import ai_bp

__all__ = ['main_bp', 'ai_bp']
