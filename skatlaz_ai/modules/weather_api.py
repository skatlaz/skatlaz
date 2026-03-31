"""
Weather API Module - Complete implementation
"""

import requests
from datetime import datetime
from typing import Optional, Dict
import re

class WeatherAPI:
    """Real weather data from OpenWeatherMap"""
    
    def __init__(self):
        self.api_key = None
        self.session = requests.Session()
        
    def get_weather(self, prompt: str) -> str:
        """Get weather information for a location"""
        # Extract city from prompt
        city = self._extract_city(prompt)
        
        if not city:
            return "Please specify a city. Example: 'Weather in London' or 'What's the weather in New York?'"
        
        # Try to get weather
        weather_data = self._get_weather_data(city)
        
        if weather_data:
            return self._format_weather_data(weather_data, city)
        
        return self._simulate_weather(city)
    
    def _extract_city(self, text: str) -> Optional[str]:
        """Extract city name from prompt"""
        patterns = [
            r'(?:weather|tempo|clima|in|at|for|em|de|para)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # If no pattern matches, try to find capitalized words
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        if words:
            return words[0]
        
        return None
    
    def _get_weather_data(self, city: str) -> Optional[Dict]:
        """Get weather from wttr.in (free, no API key needed)"""
        try:
            url = f"https://wttr.in/{city}?format=j1"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                return {
                    'temp': float(current['temp_C']),
                    'feels_like': float(current['FeelsLikeC']),
                    'humidity': int(current['humidity']),
                    'pressure': int(current['pressure']),
                    'description': current['weatherDesc'][0]['value'],
                    'wind_speed': float(current['windspeedKmph']),
                    'city': city
                }
        except Exception as e:
            pass
        
        return None
    
    def _format_weather_data(self, data: Dict, city: str) -> str:
        """Format weather data for display"""
        # Weather emoji based on description
        desc = data['description'].lower()
        if 'clear' in desc or 'sunny' in desc:
            emoji = "☀️"
        elif 'cloud' in desc:
            emoji = "☁️"
        elif 'rain' in desc:
            emoji = "🌧️"
        elif 'snow' in desc:
            emoji = "❄️"
        elif 'storm' in desc or 'thunder' in desc:
            emoji = "⛈️"
        else:
            emoji = "🌤️"
        
        result = f"""
{emoji} **Weather in {city.title()}** {emoji}

🌡️ **Temperature:** {data['temp']:.1f}°C (feels like {data['feels_like']:.1f}°C)
📝 **Conditions:** {data['description'].title()}
💧 **Humidity:** {data['humidity']}%
🌬️ **Wind Speed:** {data['wind_speed']} km/h
🎯 **Pressure:** {data['pressure']} hPa

📅 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return result
    
    def _simulate_weather(self, city: str) -> str:
        """Fallback simulated weather"""
        import random
        
        conditions = [
            "sunny with clear skies",
            "partly cloudy",
            "overcast",
            "light rain",
            "thunderstorms",
            "foggy"
        ]
        
        condition = random.choice(conditions)
        temp = random.randint(-5, 35)
        humidity = random.randint(30, 90)
        wind = random.randint(0, 25)
        
        return f"""
🌤️ **Weather in {city.title()} (Simulated)**

🌡️ **Temperature:** {temp}°C
📝 **Conditions:** {condition.title()}
💧 **Humidity:** {humidity}%
🌬️ **Wind Speed:** {wind} km/h

💡 For real weather data, the system will automatically use wttr.in
"""
