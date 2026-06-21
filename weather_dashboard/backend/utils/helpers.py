"""Helper functions for Weather Dashboard."""

from datetime import datetime
from typing import Dict, Optional


def kelvin_to_celsius(kelvin: float) -> float:
    """Convert Kelvin to Celsius."""
    return kelvin - 273.15


def kelvin_to_fahrenheit(kelvin: float) -> float:
    """Convert Kelvin to Fahrenheit."""
    return (kelvin - 273.15) * 9/5 + 32


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return celsius * 9/5 + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9


def mps_to_kmh(mps: float) -> float:
    """Convert meters per second to kilometers per hour."""
    return mps * 3.6


def mps_to_mph(mps: float) -> float:
    """Convert meters per second to miles per hour."""
    return mps * 2.237


def format_timestamp(timestamp: int) -> str:
    """Format Unix timestamp to readable string."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def format_time(timestamp: int) -> str:
    """Format Unix timestamp to time string."""
    return datetime.fromtimestamp(timestamp).strftime('%H:%M')


def format_date(timestamp: int) -> str:
    """Format Unix timestamp to date string."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')


def get_weather_icon_emoji(icon_code: str) -> str:
    """
    Convert OpenWeatherMap icon code to emoji.
    
    Args:
        icon_code: Weather icon code from API
    
    Returns:
        Corresponding emoji
    """
    icon_map = {
        '01d': '☀️',   # Clear sky (day)
        '01n': '🌙',   # Clear sky (night)
        '02d': '⛅',   # Few clouds (day)
        '02n': '☁️',   # Few clouds (night)
        '03d': '☁️',   # Scattered clouds (day)
        '03n': '☁️',   # Scattered clouds (night)
        '04d': '☁️',   # Broken clouds (day)
        '04n': '☁️',   # Broken clouds (night)
        '09d': '🌧️',   # Shower rain (day)
        '09n': '🌧️',   # Shower rain (night)
        '10d': '🌦️',   # Rain (day)
        '10n': '🌧️',   # Rain (night)
        '11d': '⛈️',   # Thunderstorm (day)
        '11n': '⛈️',   # Thunderstorm (night)
        '13d': '❄️',   # Snow (day)
        '13n': '❄️',   # Snow (night)
        '50d': '🌫️',   # Mist (day)
        '50n': '🌫️',   # Mist (night)
    }
    return icon_map.get(icon_code, '🌡️')


def get_wind_direction(degrees: int) -> str:
    """
    Convert wind direction degrees to cardinal directions.
    
    Args:
        degrees: Wind direction in degrees
    
    Returns:
        Cardinal direction (N, NE, E, etc.)
    """
    directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                  'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    index = round(degrees / 22.5) % 16
    return directions[index]


def get_uv_index_category(uv_index: float) -> str:
    """
    Categorize UV index value.
    
    Args:
        uv_index: UV index value
    
    Returns:
        UV index category
    """
    if uv_index < 3:
        return 'Low'
    elif uv_index < 6:
        return 'Moderate'
    elif uv_index < 8:
        return 'High'
    elif uv_index < 11:
        return 'Very High'
    else:
        return 'Extreme'


def get_visibility_description(visibility: int) -> str:
    """
    Describe visibility in meters.
    
    Args:
        visibility: Visibility in meters
    
    Returns:
        Visibility description
    """
    if visibility < 1000:
        return 'Very Poor'
    elif visibility < 4000:
        return 'Poor'
    elif visibility < 10000:
        return 'Moderate'
    else:
        return 'Excellent'


def format_weather_data(data: Dict) -> Dict:
    """
    Format weather data for display.
    
    Args:
        data: Raw weather data
    
    Returns:
        Formatted weather data
    """
    if not data:
        return {}
    
    return {
        **data,
        'icon_emoji': get_weather_icon_emoji(data.get('icon', '')),
        'wind_direction_text': get_wind_direction(data.get('wind_direction', 0)),
        'uv_category': get_uv_index_category(data.get('uv_index', 0)),
        'visibility_description': get_visibility_description(data.get('visibility', 10000)),
        'formatted_time': format_timestamp(data.get('last_updated', 0))
    }
