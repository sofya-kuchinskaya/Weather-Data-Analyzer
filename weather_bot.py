import analyzer as a
from dotenv import load_dotenv
import os
import telebot
from telebot import types

load_dotenv()
token = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(token)
weather_bot = a.WeatherApp()

CITIES_TEXT = """📍 *СПИСОК ГОРОДОВ ДЛЯ КОПИРОВАНИЯ*

*🇷🇺 РОССИЯ*
55.7558 37.6173 - Москва (столица)
59.9343 30.3351 - Санкт-Петербург (культурная столица)
55.0084 82.9357 - Новосибирск (крупнейший город Сибири)
56.8389 60.6057 - Екатеринбург (Урал)
55.7963 49.1064 - Казань (столица Татарстана)
43.5855 39.7231 - Сочи (курорт на Чёрном море)

*🌍 МИРОВЫЕ СТОЛИЦЫ*
51.5074 -0.1278 - Лондон (Великобритания)
48.8566 2.3522 - Париж (Франция)
40.7128 -74.0060 - Нью-Йорк (США)
35.6762 139.6503 - Токио (Япония)
-33.8688 151.2093 - Сидней (Австралия)
25.2048 55.2708 - Дубай (ОАЭ)

*📋 ИНСТРУКЦИЯ:*
1. Скопируйте нужные координаты или введите свои
2. Вставьте в следующем сообщении
3. Формат: `широта долгота`"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """🌤  *WEATHER DATA ANALYZER*

*О ПРОГРАММЕ:*
Это телеграм-бот для анализа погодных данных.
Использует Open-Meteo API для получения актуальных метеоданных.
Для более подробной информации используйте команду /help .

*ВЫБЕРИТЕ ДЕЙСТВИЕ:*"""

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    btn1 = types.KeyboardButton("1️⃣ Текущая погода")
    btn2 = types.KeyboardButton("2️⃣ График на 24ч")
    btn3 = types.KeyboardButton("3️⃣ Сравнить города")
    btn4 = types.KeyboardButton("4️⃣ Выход")

    markup.add(btn1, btn2, btn3, btn4)  


    bot.send_message(
        message.chat.id,
        welcome_text, reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """📖 *ПОЛНАЯ СПРАВКА ПО БОТУ*

*ЧТО УМЕЕТ БОТ:*

🌡 *Текущая погода* (функция 1)
• Температура воздуха
• Скорость ветра  
• Относительная влажность
• Описание погодных условий

📈 *Прогноз на 24 часа* (функция 2)
• Почасовой прогноз температуры
• График изменения

🔍 *Сравнение городов* (функция 3)
• Сравнение до 6 локаций одновременно
• Таблица с основными параметрами: температура, ветер, влажность, описание погоды
• Быстрое сравнение популярных городов

*КАК ПОЛЬЗОВАТЬСЯ:*
1. Выберите функцию (1, 2 или 3)
2. Бот покажет список городов с координатами
3. Скопируйте нужные координаты или введите вручную
4. Вставьте в следующем сообщении

*ФОРМАТ КООРДИНАТ:*
• Один город: широта долгота
• Пример: 55.7558 37.6173
• Несколько городов: широта1 долгота1 широта2 долгота2
• Пример: 55.7558 37.6173 51.5074 -0.1278

*ДОСТУПНЫЕ КОМАНДЫ:*
/start - главное меню
/help - эта справка

*ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ:*
• Используется Open-Meteo API
• Обновление данных каждые 15 минут
• Поддерживает любые координаты мира"""
    
    bot.send_message(
        message.chat.id,
        help_text,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda msg: msg.text == "1️⃣ Текущая погода")
def handle_button_current(message):
    ask_for_current_weather(message)

# Обработка кнопки "2️⃣ График на 24ч"
@bot.message_handler(func=lambda msg: msg.text == "2️⃣ График на 24ч")
def handle_button_forecast(message):
    ask_for_forecast(message)

# Обработка кнопки "3️⃣ Сравнить города"
@bot.message_handler(func=lambda msg: msg.text == "3️⃣ Сравнить города")
def handle_button_compare(message):
    ask_for_compare(message)

# Обработка кнопки "4️⃣ Выход"
@bot.message_handler(func=lambda msg: msg.text == "4️⃣ Выход")
def handle_button_exit(message):
    bot.send_message(message.chat.id, "👋 До свидания!")
    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Нажмите /start чтобы начать снова", reply_markup=markup)

def ask_for_current_weather(message):
    msg = bot.send_message(
        message.chat.id,
        CITIES_TEXT,
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_current_weather)

def process_current_weather(message):
    try:   
        coords = message.text.strip().split()
        if len(coords) != 2:
            raise ValueError()
        
        lat = float(coords[0])
        lon = float(coords[1])
        
        data = weather_bot.get_current_weather(lat, lon)
        weather_text = weather_bot.format_weather(data)
        
        response = weather_text
        
        bot.send_message(
            message.chat.id,
            response,
            parse_mode="Markdown"
        )
    except ValueError as e:
        error_msg = f"""❌ *Ошибка*

Правильный формат: широта долгота
Пример: 55.7558 37.6173

Попробуйте снова"""
        msg = bot.send_message(
            message.chat.id,
            error_msg,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_current_weather)
        
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ *Ошибка*. Попробуйте еще раз чуть позже.",
            parse_mode="Markdown"
        )

def ask_for_forecast(message): 
    msg = bot.send_message(
        message.chat.id,
        CITIES_TEXT,
        parse_mode="Markdown"
    )
    
    bot.register_next_step_handler(msg, process_forecast)

def process_forecast(message):
    try:
        coords = message.text.strip().split()
        if len(coords) != 2:
            raise ValueError()
        
        lat = float(coords[0])
        lon = float(coords[1])
        
        data = weather_bot.get_hourly_forecast(lat, lon, 24)
        
        try:
            # Получаем изображение от анализатора
            image_buffer = weather_bot.plot_forecast(data, return_image=True)
            
            # Отправляем картинку в Telegram
            bot.send_photo(
                message.chat.id,
                photo=image_buffer,
                caption="📈 График температуры на 24 часа"
            )
        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"Не удалось построить график"
            )

    except ValueError as e:
        error_msg = f"""❌ *Ошибка*

Правильный формат: широта долгота
Пример: 55.7558 37.6173 

Попробуйте снова"""
        msg = bot.send_message(
            message.chat.id,
            error_msg,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_forecast)

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка. Попробуйте еще раз чуть позже.",
            parse_mode="Markdown"
        )
        
def ask_for_compare(message):
    msg = bot.send_message(
        message.chat.id,
        CITIES_TEXT,
        parse_mode="Markdown"
    )
    
    bot.register_next_step_handler(msg, process_compare)

def process_compare(message):
    try:
        coords = message.text.strip().split()
        if len(coords) < 4 or len(coords) % 2 != 0:
            raise ValueError()
        
        locations = []
        for i in range(0, len(coords), 2):
                    locations.append(((coords[i]), (coords[i+1])))
        
        data = weather_bot.compare_locations(locations)
                
        df = weather_bot.table_comparison(data, locations)

        table_text = f"""🔍 *Сравнение {len(df)} городов:*\n\n{df.to_string(index=False)}\n"""
        
        bot.send_message(
            message.chat.id,
            table_text,
            parse_mode="Markdown"
        )
    
    except ValueError as e:
        error_msg = f"""❌ *Ошибка*

Правильный формат: широта1 долгота1 широта2 долгота2
Пример: 55.7558 37.6173 1.5074 -0.1278

Попробуйте снова"""
        msg = bot.send_message(
            message.chat.id,
            error_msg,
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_compare)
    
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка. Попробуйте еще раз чуть позже.",
            parse_mode="Markdown"
        )
 
@bot.message_handler(func=lambda msg: True)
def handle_other_messages(message): 
        bot.send_message(
            message.chat.id,


"🤔 *Не понимаю команду*\n\n"
            "Используйте команды:\n"
            "/start - показать меню с кнопками\n"
            "/help - справка по использованию\n",
            parse_mode="Markdown"
        )

if __name__ == "__main__":
    bot.polling(none_stop=True)