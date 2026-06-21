/**
 * UI Update Functions
 * Handles all DOM updates and user interactions
 */

function getWeatherEmoji(iconCode) {
    const emojiMap = {
        '01d': '☀️', '01n': '🌙',
        '02d': '⛅', '02n': '☁️',
        '03d': '☁️', '03n': '☁️',
        '04d': '☁️', '04n': '☁️',
        '09d': '🌧️', '09n': '🌧️',
        '10d': '🌦️', '10n': '🌧️',
        '11d': '⛈️', '11n': '⛈️',
        '13d': '❄️', '13n': '❄️',
        '50d': '🌫️', '50n': '🌫��',
    };
    return emojiMap[iconCode] || '🌡️';
}

function formatTemperature(temp, units) {
    if (!temp) return '-';
    const rounded = Math.round(temp * 10) / 10;
    const symbol = units === 'metric' ? '°C' : units === 'imperial' ? '°F' : 'K';
    return `${rounded}${symbol}`;
}

function updateCurrentWeather(data, units) {
    const container = document.getElementById('currentWeather');
    if (!data || !data.data) {
        container.innerHTML = '<div class="loading">Unable to load weather data</div>';
        return;
    }

    const weather = data.data;
    const html = `
        <div class="weather-display">
            <div class="weather-icon">${getWeatherEmoji(weather.icon)}</div>
            <div>
                <div class="city-name">${weather.city}, ${weather.country}</div>
                <div class="weather-description">${weather.description}</div>
                <div class="temperature-display">
                    <div class="temperature-value">${Math.round(weather.temperature)}</div>
                    <div class="temperature-unit">${units === 'metric' ? '°C' : '°F'}</div>
                </div>
            </div>
        </div>
        <div class="weather-info-grid">
            <div class="weather-info-item">
                <div class="info-label">Feels Like</div>
                <div class="info-value">${Math.round(weather.feels_like)}°</div>
            </div>
            <div class="weather-info-item">
                <div class="info-label">Humidity</div>
                <div class="info-value">${weather.humidity}%</div>
            </div>
            <div class="weather-info-item">
                <div class="info-label">Wind Speed</div>
                <div class="info-value">${weather.wind_speed.toFixed(1)} m/s</div>
            </div>
            <div class="weather-info-item">
                <div class="info-label">Pressure</div>
                <div class="info-value">${weather.pressure} mb</div>
            </div>
        </div>
    `;
    container.innerHTML = html;

    // Update details section
    document.getElementById('feelsLike').textContent = formatTemperature(weather.feels_like, units);
    document.getElementById('humidity').textContent = weather.humidity + '%';
    document.getElementById('windSpeed').textContent = weather.wind_speed.toFixed(1) + ' m/s';
    document.getElementById('pressure').textContent = weather.pressure + ' mb';
    document.getElementById('visibility').textContent = (weather.visibility / 1000).toFixed(1) + ' km';
    document.getElementById('uvIndex').textContent = weather.uv_index ? weather.uv_index.toFixed(1) : 'N/A';

    // Store current weather for favorites
    window.currentWeatherData = { ...weather, units };
}

function updateForecast(data, units) {
    const container = document.getElementById('forecast');
    if (!data || !data.data || !data.data.forecasts) {
        container.innerHTML = '<div class="loading">Unable to load forecast</div>';
        return;
    }

    const forecasts = data.data.forecasts;
    let html = '';

    // Group by day and take every 8th item (one per day)
    const dailyForecasts = forecasts.filter((_, index) => index % 8 === 0).slice(0, 5);

    dailyForecasts.forEach(forecast => {
        const date = new Date(forecast.timestamp * 1000);
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dayDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

        html += `
            <div class="forecast-card">
                <div class="forecast-time">${dayName}<br>${dayDate}</div>
                <div class="forecast-icon">${getWeatherEmoji(forecast.icon)}</div>
                <div class="forecast-temp">${Math.round(forecast.temperature)}°</div>
                <div class="forecast-description">${forecast.description}</div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function displaySearchResults(results) {
    const container = document.getElementById('searchResults');
    if (!results || results.length === 0) {
        container.style.display = 'none';
        return;
    }

    let html = '';
    results.forEach(result => {
        html += `
            <div class="search-result-item" onclick="selectCity('${result.name}', '${result.country}')">
                <strong>${result.name}</strong><br>
                <small>${result.country}${result.state ? ', ' + result.state : ''}</small>
            </div>
        `;
    });

    container.innerHTML = html;
    container.style.display = 'block';
}

function hideSearchResults() {
    document.getElementById('searchResults').style.display = 'none';
}

async function selectCity(city, country) {
    hideSearchResults();
    document.getElementById('searchInput').value = '';
    await loadWeather(city);
}

function toggleDarkMode() {
    const isDark = document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', isDark ? 'true' : 'false');
    document.getElementById('darkModeToggle').textContent = isDark ? '☀️' : '🌙';
}

function initDarkMode() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = localStorage.getItem('darkMode') === 'true' || (!localStorage.getItem('darkMode') && prefersDark);
    if (isDark) {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').textContent = '☀️';
    }
}

function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}
