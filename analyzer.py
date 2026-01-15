import requests
import pandas as pd
import matplotlib
import matplotlib.pyplot  as plt


cities = [
    ("Москва", "55.7558 37.6173"),
    ("Санкт-Петербург", "59.9343 30.3351"),
    ("Новосибирск", "55.0084 82.9357"),
    ("Екатеринбург", "56.8389 60.6057"),
    ("Казань", "55.7963 49.1064"),
    ("Сочи", "43.5855 39.7231"),
    ("Лондон", "51.5074 -0.1278"),
    ("Париж", "48.8566 2.3522"),
    ("Нью-Йорк", "40.7128 -74.0060"),
    ("Токио", "35.6762 139.6503"),
    ("Сидней", "-33.8688 151.2093"),
    ("Дубай", "25.2048 55.2708")
]

class WeatherApp:
    """Полный погодный анализатор в одном классе"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.weather_codes = {
            0: "Ясно ☀️",
    1: "Преимущественно ясно 🌤",
    2: "Переменная облачность ⛅", 
    3: "Пасмурно ☁️",
    45: "Туман 🌫️",
    48: "Изморозь ❄️",
    51: "Легкая морось 🌧️",
    53: "Умеренная морось 🌧️",
    55: "Сильная морось 🌧️",
    56: "Ледяная морось 🌧️❄️",
    57: "Сильная ледяная морось 🌧️❄️",
    61: "Небольшой дождь 🌦️",
    63: "Умеренный дождь 🌧️",
    65: "Сильный дождь ⛈️",
    66: "Ледяной дождь 🌧️❄️",
    67: "Сильный ледяной дождь 🌧️❄️",
    71: "Небольшой снег 🌨️",
    73: "Умеренный снег 🌨️",
    75: "Сильный снег ❄️",
    77: "Снежные зерна ❄️",
    80: "Небольшие ливни 🌦️",
    81: "Умеренные ливни 🌧️",
    82: "Сильные ливни ⛈️",
    85: "Небольшие снегопады 🌨️",
    86: "Сильные снегопады ❄️",
    95: "Гроза ⛈️",
    96: "Гроза с градом 🌩️",
    99: "Сильная гроза с градом 🌩️⛈️"
}
    def get_current_weather(self, lat: float, lon: float) -> dict:
        """Функция 1: Текущая погода"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
            "timezone": "auto"
        }
        response = requests.get(self.base_url, params=params, timeout=10)
        return response.json()
    
    def get_hourly_forecast(self, lat: float, lon: float, hours: int = 24) -> dict:
        """Функция 2: Почасовой прогноз"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
            "forecast_days": 1,
            "timezone": "auto"
        }
        response = requests.get(self.base_url, params=params, timeout=10)
        return response.json()
    
    def compare_locations(self, locations: list) -> dict:
        """Функция 3: Сравнение локаций"""
        lats = [loc[0] for loc in locations]
        lons = [loc[1] for loc in locations]
        
        params = {
            "latitude": ",".join(lats),
            "longitude": ",".join(lons),
            "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
            "timezone": "auto"
        }
        response = requests.get(self.base_url, params=params, timeout=10)
        return response.json()
    
    def format_weather(self, data: dict) -> str:
        """Красивый вывод текущей погоды"""
        current = data.get('current', {})
        code = current.get('weather_code', 0)
        
        return f"""
📍 ТЕКУЩАЯ ПОГОДА
{'='*30}
🌡  Температура: {current.get('temperature_2m', 'N/A')}°C
💨 Ветер: {current.get('wind_speed_10m', 'N/A')} км/ч
💧 Влажность: {current.get('relative_humidity_2m', 'N/A')}%
☁  {self.weather_codes.get(code)}
{'='*30}
        """
    
    def plot_forecast(self, data: dict, return_image=False):
        hourly = data.get('hourly', {})
        
        df = pd.DataFrame({
            'time': pd.to_datetime(hourly.get('time', [])),
            'temperature': hourly.get('temperature_2m', [])
        })
        
        df.plot(
            x='time',                    
            y='temperature',             
            kind='line', figsize=(12, 6))
        
        if return_image:
            import io
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()
            return buf
        else:
            plt.show()
    
    def table_comparison(self, data: dict, locations: list):
        table_rows = []
        for i in range(len(locations)):
                    lat, lon = locations[i]
                    city = data[i]
                    current = city.get('current', {})
                    table_rows.append({
                'Координаты': f"({lat}, {lon})",
                'Температура': f"{current.get('temperature_2m', 'N/A')}°C",
                'Влажность': f"{current.get('relative_humidity_2m', 'N/A')}%",
                'Ветер': f"{current.get('wind_speed_10m', 'N/A')} км/ч",
                'Погода': self.weather_codes.get(
                    current.get('weather_code', 0),
                )
            })
        df = pd.DataFrame(table_rows)
        return df

    
    def run(self):
        print("=" * 50)
        print("🌤  WEATHER DATA ANALYZER")
        print("=" * 50)
        
        while True:
            print("\n1. Текущая погода")
            print("2. График на 24 часа")
            print("3. Сравнить города")
            print("4. Выход")
            
            choice = input("\nВыберите: ").strip()
            
            if choice == "1":
                print("Вы можете скопировать координаты отсюда или задать свои:")
                for city in cities:
                    print(city)
                lat = float(input("Широта: "))
                lon = float(input("Долгота: "))
                data = self.get_current_weather(lat, lon)
                print(self.format_weather(data))
            
            elif choice == "2":
                print("Вы можете скопировать координаты отсюда или задать свои:")
                for city in cities:
                    print(city)
                lat = float(input("Широта: "))
                lon = float(input("Долгота: "))
                data = self.get_hourly_forecast(lat, lon, 24)
                self.plot_forecast(data)
            
            elif choice == "3":
                print("Вы можете скопировать координаты отсюда или задать свои:")
                for city in cities:
                    print(city)
                print("Введите координаты через пробел:")
                print("Пример: 55.7558 37.6173  51.5074 -0.1278")
                coords = input("> ").strip().split()
                locations = []
                
                for i in range(0, len(coords), 2):
                    locations.append(((coords[i]), (coords[i+1])))
                
                data = self.compare_locations(locations)
                print("\n" + "="*40)
                print("📊 ТАБЛИЦА СРАВНЕНИЯ:")
                print(self.table_comparison(data, locations))
                print("="*40)
            
            elif choice == "4":
                print("👋 До свидания!")
                break
            
            else:
                print("❌ Неверный выбор")
            
            input("\nEnter для продолжения...")      


if __name__ == "__main__":
    app = WeatherApp()
    app.run()

