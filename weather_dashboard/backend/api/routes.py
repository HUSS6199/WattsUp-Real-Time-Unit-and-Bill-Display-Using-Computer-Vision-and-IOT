"""Flask routes for Weather Dashboard API."""

from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


def handle_errors(f):
    """Decorator for error handling in API routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e), 'code': 'INVALID_PARAMS'}), 400
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {e}")
            return jsonify({'success': False, 'error': 'Internal server error', 'code': 'SERVER_ERROR'}), 500
    return decorated_function


@api_bp.route('/weather/current', methods=['GET'])
@handle_errors
def get_current_weather():
    """
    Get current weather for a city.
    
    Query Parameters:
        - city: City name (required)
        - units: metric (default), imperial, standard
    """
    from backend.api.weather import WeatherAPI
    from backend.utils.cache import get_cached, set_cached
    
    city = request.args.get('city', '').strip()
    units = request.args.get('units', 'metric').lower()
    
    if not city:
        return jsonify({'success': False, 'error': 'City parameter required', 'code': 'INVALID_PARAMS'}), 400
    
    if units not in current_app.config['SUPPORTED_UNITS']:
        return jsonify({'success': False, 'error': f'Units must be one of {current_app.config["SUPPORTED_UNITS"]}', 'code': 'INVALID_PARAMS'}), 400
    
    # Check cache
    cache_key = f"weather_current_{city}_{units}"
    cached_data = get_cached(cache_key)
    if cached_data:
        return jsonify({'success': True, 'data': cached_data, 'cached': True})
    
    # Fetch from API
    api = WeatherAPI(current_app.config['OPENWEATHER_API_KEY'])
    weather = api.get_current_weather(city, units)
    
    if not weather:
        return jsonify({'success': False, 'error': 'City not found', 'code': 'NOT_FOUND'}), 404
    
    # Cache the result
    set_cached(cache_key, weather, current_app.config['CACHE_CURRENT_WEATHER'])
    
    return jsonify({'success': True, 'data': weather})


@api_bp.route('/weather/current/coords', methods=['GET'])
@handle_errors
def get_current_weather_coords():
    """
    Get current weather by coordinates.
    
    Query Parameters:
        - lat: Latitude (required)
        - lon: Longitude (required)
        - units: metric (default), imperial, standard
    """
    from backend.api.weather import WeatherAPI
    from backend.utils.cache import get_cached, set_cached
    
    try:
        lat = float(request.args.get('lat', 0))
        lon = float(request.args.get('lon', 0))
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid latitude or longitude', 'code': 'INVALID_PARAMS'}), 400
    
    units = request.args.get('units', 'metric').lower()
    
    if units not in current_app.config['SUPPORTED_UNITS']:
        return jsonify({'success': False, 'error': f'Units must be one of {current_app.config["SUPPORTED_UNITS"]}', 'code': 'INVALID_PARAMS'}), 400
    
    # Check cache
    cache_key = f"weather_coords_{lat}_{lon}_{units}"
    cached_data = get_cached(cache_key)
    if cached_data:
        return jsonify({'success': True, 'data': cached_data, 'cached': True})
    
    # Fetch from API
    api = WeatherAPI(current_app.config['OPENWEATHER_API_KEY'])
    weather = api.get_current_weather_by_coords(lat, lon, units)
    
    if not weather:
        return jsonify({'success': False, 'error': 'Unable to fetch weather data', 'code': 'API_ERROR'}), 500
    
    # Cache the result
    set_cached(cache_key, weather, current_app.config['CACHE_CURRENT_WEATHER'])
    
    return jsonify({'success': True, 'data': weather})


@api_bp.route('/weather/forecast', methods=['GET'])
@handle_errors
def get_forecast():
    """
    Get 5-day forecast for a city.
    
    Query Parameters:
        - city: City name (required)
        - units: metric (default), imperial, standard
    """
    from backend.api.weather import WeatherAPI
    from backend.utils.cache import get_cached, set_cached
    
    city = request.args.get('city', '').strip()
    units = request.args.get('units', 'metric').lower()
    
    if not city:
        return jsonify({'success': False, 'error': 'City parameter required', 'code': 'INVALID_PARAMS'}), 400
    
    if units not in current_app.config['SUPPORTED_UNITS']:
        return jsonify({'success': False, 'error': f'Units must be one of {current_app.config["SUPPORTED_UNITS"]}', 'code': 'INVALID_PARAMS'}), 400
    
    # Check cache
    cache_key = f"weather_forecast_{city}_{units}"
    cached_data = get_cached(cache_key)
    if cached_data:
        return jsonify({'success': True, 'data': cached_data, 'cached': True})
    
    # Fetch from API
    api = WeatherAPI(current_app.config['OPENWEATHER_API_KEY'])
    forecast = api.get_forecast(city, units)
    
    if not forecast:
        return jsonify({'success': False, 'error': 'City not found', 'code': 'NOT_FOUND'}), 404
    
    # Cache the result
    set_cached(cache_key, forecast, current_app.config['CACHE_FORECAST'])
    
    return jsonify({'success': True, 'data': forecast})


@api_bp.route('/weather/search', methods=['GET'])
@handle_errors
def search_cities():
    """
    Search for cities by name.
    
    Query Parameters:
        - query: Search query (required)
    """
    from backend.api.weather import WeatherAPI
    from backend.utils.cache import get_cached, set_cached
    
    query = request.args.get('query', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'success': False, 'error': 'Query must be at least 2 characters', 'code': 'INVALID_PARAMS'}), 400
    
    # Check cache
    cache_key = f"weather_search_{query}"
    cached_data = get_cached(cache_key)
    if cached_data:
        return jsonify({'success': True, 'data': cached_data, 'cached': True})
    
    # Fetch from API
    api = WeatherAPI(current_app.config['OPENWEATHER_API_KEY'])
    results = api.get_geocoding(query, limit=5)
    
    if not results:
        return jsonify({'success': True, 'data': []})
    
    # Format results
    formatted = [{
        'name': r.get('name', ''),
        'country': r.get('country', ''),
        'latitude': r.get('lat'),
        'longitude': r.get('lon'),
        'state': r.get('state', '')
    } for r in results]
    
    # Cache the result
    set_cached(cache_key, formatted, current_app.config['CACHE_LOCATION_SEARCH'])
    
    return jsonify({'success': True, 'data': formatted})


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
