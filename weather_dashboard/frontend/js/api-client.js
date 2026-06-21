/**
 * Weather API Client
 * Handles all API communication with the backend
 */

class WeatherAPIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.timeout = 10000;
    }

    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'API request failed');
            }

            return data;
        } catch (error) {
            console.error(`API Error: ${endpoint}`, error);
            throw error;
        }
    }

    /**
     * Get current weather for a city
     */
    async getCurrentWeather(city, units = 'metric') {
        return this.request(`/weather/current?city=${encodeURIComponent(city)}&units=${units}`);
    }

    /**
     * Get current weather by coordinates
     */
    async getCurrentWeatherByCoords(lat, lon, units = 'metric') {
        return this.request(`/weather/current/coords?lat=${lat}&lon=${lon}&units=${units}`);
    }

    /**
     * Get 5-day forecast
     */
    async getForecast(city, units = 'metric') {
        return this.request(`/weather/forecast?city=${encodeURIComponent(city)}&units=${units}`);
    }

    /**
     * Search cities
     */
    async searchCities(query) {
        if (query.length < 2) {
            return { success: true, data: [] };
        }
        return this.request(`/weather/search?query=${encodeURIComponent(query)}`);
    }

    /**
     * Get configuration
     */
    async getConfig() {
        return this.request('/config');
    }
}

// Create global API client instance
const apiClient = new WeatherAPIClient();
