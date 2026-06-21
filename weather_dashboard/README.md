# Weather Dashboard

A modern, responsive weather dashboard that fetches real-time weather data from OpenWeatherMap API and displays current conditions, forecasts, and weather alerts.

## Features

- 🌍 **Real-time Weather Data** - Current conditions for any city worldwide
- 📊 **5-Day Forecast** - Hourly and daily forecasts with visual indicators
- 🚨 **Weather Alerts** - Severe weather warnings and notifications
- 📍 **Geolocation Support** - Auto-detect location or search by city
- 🎨 **Responsive UI** - Works on desktop, tablet, and mobile devices
- 🌙 **Dark Mode** - Easy on the eyes during night hours
- 📈 **Weather Charts** - Temperature, humidity, and pressure trends
- 💾 **Local Storage** - Remember favorite locations
- ⚡ **Fast Performance** - Cached data with background refresh

## Tech Stack

### Backend
- **Python 3.9+**
- **Flask** - Web framework
- **Requests** - HTTP client for API calls
- **OpenWeatherMap API** - Weather data source
- **SQLite** - Local data storage

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Responsive design with Flexbox/Grid
- **JavaScript (Vanilla)** - Interactivity and real-time updates
- **Chart.js** - Weather trend visualization

## Prerequisites

1. **Python 3.9+**
2. **pip** (Python package manager)
3. **OpenWeatherMap API Key** (free at https://openweathermap.org/api)
4. **Modern web browser** (Chrome, Firefox, Safari, Edge)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/HUSS6199/weather-dashboard.git
cd weather_dashboard
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```
OPENWEATHER_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

Get your free API key:
1. Visit https://openweathermap.org/api
2. Sign up for a free account
3. Generate an API key
4. Add it to `.env`

### 5. Initialize Database
```bash
python3 backend/init_db.py
```

### 6. Run the Application
```bash
python3 backend/app.py
```

Open your browser to `http://localhost:5000`

## Project Structure

```
weather_dashboard/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration settings
│   ├── init_db.py             # Database initialization
│   ├── requirements.txt        # Python dependencies
│   ├── api/
│   │   ├── __init__.py
│   │   ├── weather.py         # OpenWeatherMap API wrapper
│   │   └── routes.py          # Flask routes (API endpoints)
│   ├── models/
│   │   ├── __init__.py
│   │   └── location.py        # Location model & database
│   └── utils/
│       ├── __init__.py
│       ├── cache.py           # Caching utilities
│       └── helpers.py         # Helper functions
├── frontend/
│   ├── index.html             # Main dashboard page
│   ├── css/
│   │   ├── style.css          # Main stylesheet
│   │   └── responsive.css     # Mobile responsiveness
│   └── js/
│       ├── main.js            # Main application logic
│       ├── api-client.js      # API communication
│       ├── ui.js              # UI update functions
│       └── charts.js          # Chart initialization
├── tests/
│   ├── test_weather_api.py
│   ├── test_routes.py
│   └── test_cache.py
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## API Endpoints

### Weather Endpoints

#### Get Current Weather
```
GET /api/weather/current?city=London&units=metric
```

**Response:**
```json
{
  "success": true,
  "data": {
    "city": "London",
    "country": "GB",
    "temperature": 15.2,
    "feels_like": 14.8,
    "humidity": 65,
    "pressure": 1013,
    "description": "Partly cloudy",
    "icon": "02d",
    "wind_speed": 5.2,
    "wind_direction": 230,
    "cloudiness": 30,
    "visibility": 10000,
    "uv_index": 3,
    "sunrise": 1621000800,
    "sunset": 1621058400,
    "last_updated": 1621034400
  }
}
```

#### Get 5-Day Forecast
```
GET /api/weather/forecast?city=London&units=metric
```

#### Get Weather Alerts
```
GET /api/weather/alerts?city=London
```

#### Search Cities
```
GET /api/weather/search?query=Lon
```

### Location Endpoints

#### Save Favorite Location
```
POST /api/locations/favorite
```

**Request Body:**
```json
{
  "city": "London",
  "country": "GB",
  "latitude": 51.5074,
  "longitude": -0.1278
}
```

#### Get Favorite Locations
```
GET /api/locations/favorites
```

#### Delete Favorite Location
```
DELETE /api/locations/favorite/1
```

## Configuration

### Units
- `metric` - Celsius (default)
- `imperial` - Fahrenheit
- `standard` - Kelvin

### Update Intervals
- Current weather: 10 minutes
- Forecast: 30 minutes
- Alerts: 5 minutes

### Cache Settings
- Current weather cache: 10 minutes
- Forecast cache: 30 minutes
- Location search cache: 1 hour

## Usage Examples

### JavaScript - Fetch Current Weather
```javascript
const client = new WeatherAPIClient();

client.getCurrentWeather('London', 'metric')
  .then(data => {
    console.log(`Current temperature in ${data.city}: ${data.temperature}°C`);
    updateUI(data);
  })
  .catch(error => console.error('Error:', error));
```

### Python - Fetch Weather Data
```python
from backend.api.weather import WeatherAPI

api = WeatherAPI('your_api_key')
weather = api.get_current_weather('London', units='metric')
print(f"Temperature: {weather['temperature']}°C")
```

## Error Handling

All API responses include error information:

```json
{
  "success": false,
  "error": "City not found",
  "code": "NOT_FOUND"
}
```

### Common Error Codes
- `NOT_FOUND` - City/location not found
- `API_ERROR` - OpenWeatherMap API error
- `INVALID_PARAMS` - Invalid request parameters
- `RATE_LIMIT` - API rate limit exceeded
- `SERVER_ERROR` - Internal server error

## Performance Optimization

1. **Response Caching** - Frequently accessed data cached in memory
2. **Database Indexing** - Optimized queries for location lookup
3. **Lazy Loading** - Charts and additional data load on demand
4. **API Rate Limiting** - Prevent excessive API calls
5. **Minified Assets** - Compressed CSS and JavaScript
6. **Image Optimization** - Weather icons optimized for web

## Deployment

### Heroku
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Docker
```bash
docker build -t weather-dashboard .
docker run -p 5000:5000 -e OPENWEATHER_API_KEY=xxx weather-dashboard
```

### PythonAnywhere
1. Upload files to PythonAnywhere
2. Create virtual environment
3. Set environment variables in settings
4. Reload web app

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific tests:
```bash
pytest tests/test_weather_api.py -v
```

With coverage:
```bash
pytest --cov=backend tests/
```

## Troubleshooting

### API Key Not Working
- Verify the API key in `.env` is correct
- Check that your account is activated on openweathermap.org
- Ensure you're using the correct API endpoint

### No Data Displayed
- Check browser console for JavaScript errors
- Verify backend server is running (`python3 backend/app.py`)
- Check network tab in browser DevTools for API responses
- Confirm `.env` file is in the correct location

### Slow Performance
- Check cache hit rates in server logs
- Monitor API call frequency
- Consider increasing cache durations
- Check database query performance

### Location Not Found
- Verify city name spelling
- Try with country code (e.g., "London, GB")
- Use geolocation feature for automatic detection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Open a GitHub Issue
- Check existing documentation
- Review API documentation at https://openweathermap.org/api

## Weather Icons

Weather conditions are represented by icons from OpenWeatherMap:
- ☀️ Clear sky
- ⛅ Few clouds
- ☁️ Scattered clouds
- 🌧️ Rain
- ⛈️ Thunderstorm
- ❄️ Snow
- 🌫️ Mist

## Future Enhancements

- [ ] Air quality index (AQI) integration
- [ ] Pollen count data
- [ ] Historical weather data
- [ ] Weather radar integration
- [ ] Multiple language support
- [ ] Push notifications for alerts
- [ ] Weather comparison between cities
- [ ] Calendar integration for event planning
