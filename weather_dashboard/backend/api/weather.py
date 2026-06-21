"""OpenWeatherMap API wrapper."""

import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WeatherAPI:
    """Wrapper for OpenWeatherMap API calls."""
    
    def __init__(self, api_key: str, base_url: str = 'https://api.openweathermap.org/data/2.5'):
        """
        Initialize Weather API.
        
        Args:
            api_key: OpenWeatherMap API key
            base_url: Base URL for API calls
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = 10
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make HTTP request to OpenWeatherMap API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
        
        Returns:
            JSON response or None on error
        """
        if params is None:
            params = {}
        
        params['appid'] = self.api_key
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_current_weather(self, city: str, units: str = 'metric') -> Optional[Dict]:
        """
        Get current weather for a city.
        
        Args:
            city: City name
            units: Units (metric, imperial, standard)
        
        Returns:
            Weather data dict or None
        """
        data = self._make_request('/weather', {
            'q': city,
            'units': units
        })
        
        if not data:
            return None
        
        return self._parse_current_weather(data)
    
    def get_current_weather_by_coords(self, lat: float, lon: float, units: str = 'metric') -> Optional[Dict]:
        """
        Get current weather by coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            units: Units (metric, imperial, standard)
        
        Returns:
            Weather data dict or None
        """
        data = self._make_request('/weather', {
            'lat': lat,
            'lon': lon,
            'units': units
        })
        
        if not data:
            return None
        
        return self._parse_current_weather(data)
    
    def get_forecast(self, city: str, units: str = 'metric') -> Optional[Dict]:
        """
        Get 5-day forecast for a city.
        
        Args:
            city: City name
            units: Units (metric, imperial, standard)
        
        Returns:
            Forecast data dict or None
        """
        data = self._make_request('/forecast', {
            'q': city,
            'units': units,
            'cnt': 40  # 5 days (8 forecasts per day)
        })
        
        if not data:
            return None
        
        return self._parse_forecast(data)
    
    def get_alerts(self, lat: float, lon: float) -> Optional[List[Dict]]:
        """
        Get weather alerts for location.
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            List of alerts or None
        """
        data = self._make_request('/onecall', {
            'lat': lat,
            'lon': lon,
            'exclude': 'minutely,hourly,daily'
        })
        
        if not data or 'alerts' not in data:
            return []
        
        return data['alerts']
    
    def get_geocoding(self, city: str, limit: int = 5) -> Optional[List[Dict]]:
        """
        Get coordinates for city name.
        
        Args:
            city: City name
            limit: Max number of results
        
        Returns:
            List of location dicts or None
        """
        url = 'https://api.openweathermap.org/geo/1.0/direct'
        params = {
            'q': city,
            'limit': limit,
            'appid': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding request failed: {e}")
            return None
    
    def _parse_current_weather(self, data: Dict) -> Dict:
        """
        Parse current weather response.
        
        Args:
            data: Raw API response
        
        Returns:
            Parsed weather data
        """
        return {
            'city': data.get('name', ''),
            'country': data.get('sys', {}).get('country', ''),
            'latitude': data.get('coord', {}).get('lat'),
            'longitude': data.get('coord', {}).get('lon'),
            'temperature': data.get('main', {}).get('temp'),
            'feels_like': data.get('main', {}).get('feels_like'),
            'temp_min': data.get('main', {}).get('temp_min'),
            'temp_max': data.get('main', {}).get('temp_max'),
            'humidity': data.get('main', {}).get('humidity'),
            'pressure': data.get('main', {}).get('pressure'),
            'description': data.get('weather', [{}])[0].get('main', ''),
            'icon': data.get('weather', [{}])[0].get('icon', ''),
            'wind_speed': data.get('wind', {}).get('speed'),
            'wind_direction': data.get('wind', {}).get('deg'),
            'cloudiness': data.get('clouds', {}).get('all', 0),
            'visibility': data.get('visibility'),
            'uv_index': data.get('uvi'),
            'sunrise': data.get('sys', {}).get('sunrise'),
            'sunset': data.get('sys', {}).get('sunset'),
            'timezone': data.get('timezone'),
            'rain': data.get('rain', {}).get('1h', 0),
            'snow': data.get('snow', {}).get('1h', 0),
            'last_updated': data.get('dt')
        }
    
    def _parse_forecast(self, data: Dict) -> Dict:
        """
        Parse forecast response.
        
        Args:
            data: Raw API response
        
        Returns:
            Parsed forecast data
        """
        forecasts = []
        
        for item in data.get('list', []):
            forecasts.append({
                'timestamp': item.get('dt'),
                'temperature': item.get('main', {}).get('temp'),
                'feels_like': item.get('main', {}).get('feels_like'),
                'temp_min': item.get('main', {}).get('temp_min'),
                'temp_max': item.get('main', {}).get('temp_max'),
                'humidity': item.get('main', {}).get('humidity'),
                'pressure': item.get('main', {}).get('pressure'),
                'description': item.get('weather', [{}])[0].get('main', ''),
                'icon': item.get('weather', [{}])[0].get('icon', ''),
                'wind_speed': item.get('wind', {}).get('speed'),
                'cloudiness': item.get('clouds', {}).get('all', 0),
                'visibility': item.get('visibility'),
                'rain': item.get('rain', {}).get('3h', 0),
                'snow': item.get('snow', {}).get('3h', 0),
                'pop': item.get('pop', 0)  # Probability of precipitation
            })
        
        return {
            'city': data.get('city', {}).get('name', ''),
            'country': data.get('city', {}).get('country', ''),
            'latitude': data.get('city', {}).get('coord', {}).get('lat'),
            'longitude': data.get('city', {}).get('coord', {}).get('lon'),
            'forecasts': forecasts
        }
