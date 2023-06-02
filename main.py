import telebot
from pyowm import OWM
import pandas as pd
import matplotlib.pyplot as plt
import datetime



# Вставьте свой токен Telegram-бота
TOKEN = 'YOUR_TOKEN'

# Вставьте свой токен OWM API
OWM_API_KEY = 'Your_key'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Создание экземпляра OWM
owm = OWM(OWM_API_KEY)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! Я бот погоды. Введите название города, чтобы получить прогноз погоды.')



@bot.message_handler(func=lambda message: True)
def get_weather(message):
    city = message.text

    try:
        mgr = owm.weather_manager()

        # Получение текущего прогноза
        observation = mgr.weather_at_place(city)
        w = observation.weather

        # Получение прогноза погоды на 5 дней с интервалом в 3 часа
        forecaster = mgr.forecast_at_place(city, '3h')
        forecast = forecaster.forecast

        # Создание DataFrame для хранения погодных данных
        current_data = {
            'Параметр': ['Температура:', 'Ощущается как:', 'Скорость ветра:', 'Направление ветра:', 'Влажность:', 'Давление:',
                         'Облачность:'],
            'Значение': [w.temperature('celsius')['temp'], w.temperature('celsius')['feels_like'], w.wind()['speed'],
                         w.wind()['deg'], w.humidity, w.pressure['press'], w.clouds]}
        current_df = pd.DataFrame(current_data)

        forecast_data = []
        for weather in forecast:
            time = datetime.datetime.fromtimestamp(weather.reference_time()).strftime('%d, %H:%M')
            temp = weather.temperature('celsius')['temp']
            forecast_data.append({'Время': time, 'Температура': temp})

        forecast_df = pd.DataFrame(forecast_data)

        # Построение графика
        plt.figure(figsize=(10, 5))
        plt.plot(forecast_df['Время'], forecast_df['Температура'], marker='o')
        plt.xlabel('Время')
        plt.ylabel('Температура (°C)')
        plt.title(f'Прогноз погоды на 5 дней ({city})')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Сохранение графика в файл
        plt.savefig('forecast_plot.png')

        # Преобразование DataFrame в текстовое сообщение
        weather_text = f"Погода в {city}:\n\n"
        weather_text += current_df.to_string(index=False, header=False)

        bot.reply_to(message, weather_text)

        # Отправка графика пользователю
        with open('forecast_plot.png', 'rb') as plot:
            bot.send_photo(message.chat.id, plot)
    except:
        bot.reply_to(message, 'К сожалению, не удалось получить погоду для данного города.')


# Запуск бота
bot.infinity_polling()
