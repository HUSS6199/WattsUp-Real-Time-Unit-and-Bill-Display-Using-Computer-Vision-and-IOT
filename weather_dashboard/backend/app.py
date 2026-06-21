"""Flask application for Weather Dashboard."""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import logging
import os
from pathlib import Path

from backend.config import get_config
from backend.api.routes import api_bp

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """
    Create and configure Flask application.
    
    Args:
        config: Configuration object
    
    Returns:
        Flask application instance
    """
    # Determine template folder
    base_dir = Path(__file__).resolve().parent.parent
    template_folder = str(base_dir / 'frontend')
    static_folder = str(base_dir / 'frontend')
    
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    
    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # Enable CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    
    # Check API key
    if not app.config.get('OPENWEATHER_API_KEY'):
        logger.warning('OPENWEATHER_API_KEY not set. API calls will fail.')
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Routes
    @app.route('/')
    def index():
        """Serve main dashboard page."""
        return render_template('index.html')
    
    @app.route('/api/config', methods=['GET'])
    def get_config_endpoint():
        """Get frontend configuration."""
        return jsonify({
            'units': app.config.get('DEFAULT_UNITS', 'metric'),
            'supported_units': app.config.get('SUPPORTED_UNITS', ['metric', 'imperial', 'standard'])
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'success': False, 'error': 'Not found', 'code': 'NOT_FOUND'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors."""
        logger.error(f"Server error: {error}")
        return jsonify({'success': False, 'error': 'Internal server error', 'code': 'SERVER_ERROR'}), 500
    
    logger.info('Flask application created successfully')
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
