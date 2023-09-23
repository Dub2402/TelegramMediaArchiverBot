# Импортируем telebot для работы телеграмм - бота.
import telebot
# Импортируем types из библиотеки telebot для создания кнопок.
from telebot import types
# Импортируем settings для работы бота, хранится токен.
from settings import *
# Импортируем requests для отправки запросов.
import requests
# Импортируем os для работы с локальным хранилищем фото.
import os

# Токен для работы определенного бота телегамм.
bot = telebot.TeleBot(token)


# Обработчик команды start.
@bot.message_handler(commands=['start'])
# Функция, выводящая приветствие и кнопку для дальнейшей работы бота.
def start(message):
    # Создание глобальной переменной markup.
    global markup
    # Создание ReplyKeyboardMarkup клавиатуры с изменением размера кнопок в зависимости от устройства.
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(
        types.KeyboardButton('📦 Начать сбор коллекции'))
    # Отправка ботом вступительного сообщения и кнопочек.
    bot.send_message(message.chat.id, 
                     'Здравствуйте! Я - бот, который облегчит вам сохранение фото и видео из сообщений.\nДля начала работы, нажмите на кнопку: 📦 Начать сбор коллекции.',
                       reply_markup = markup)


# Обработчик текста.
@bot.message_handler(content_types=['text'])
# Функция, выводящая ответ бота в ответ на текст.
def bot_message(message):
    # Если вызвана текст '📦 Начать сбор коллекции':
    if message.text == '📦 Начать сбор коллекции':
        # Вывод кнопки ⛔️ Остановить сбор коллекции
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('⛔️ Остановить сбор коллекции'))
        # Отправка ботом сообщения и отображение кнопки(⛔️ Остановить сбор коллекции).
        bot.send_message(message.chat.id, 'Пришлите мне сообщение с медиафайлами. Вы также можете остановить сбор коллекции и закончить работу бота.', reply_markup=markup1)
    else:
        # Отправка ботом сообщения и отображение кнопки(📦 Начать сбор коллекции).
        bot.send_message(message.chat.id, 'Формирование коллекции сброшено. Вы можете вернуться к коллекционированию позже.', reply_markup=markup)

# Обработчик фото и видео (в будущем возможно добавление: 'document', 'audio').
@bot.message_handler(content_types=['photo', 'video'])
# Сохранение фото/видео.
def bot_message(message):
    # Получение id изображения.
    photo_id = message.photo[-1].file_id 
    # Получение данных фотографии.
    file_info = bot.get_file(photo_id) 
    # Отпраляем запрос, для получения фото.
    file = requests.get(f'https://api.telegram.org/file/bot{token}/{file_info.file_path}') 
    # Даем название изображениям.
    file_name = 'photo' + message.photo[-1].file_id + '.jpg' 
    # Открываем файл фотографии.
    with open(f'upload/{file_name}', 'wb') as f:
        # Сохраняем изображение.
        f.write(file.content) 
    # Количество изображений в папке.
    number_files = len(os.listdir('upload'))
    # Вывод информации об успешности операции и количестве добавленных фотографий.
    bot.send_message(message.chat.id, f'В коллекцию добавлено {number_files} изображений.')
    
   

# Запуск работы кода.
if __name__ == "__main__":
    # Опрос серверов Telegram на предмет новых сообщений.
    bot.polling(none_stop=True)