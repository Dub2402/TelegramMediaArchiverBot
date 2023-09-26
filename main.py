#!/usr/bin/python

# Импортируем telebot для работы телеграмм - бота.
import telebot
# Импортируем types из библиотеки telebot для создания кнопок.
from telebot import types
# Импортируем requests для отправки запросов.
import requests
# Импортируем os для работы с локальным хранилищем фото.
import os
# Импортируем fnmatch для фильтрации по расширению файла.
import fnmatch
# Импортируем shutil для архивации файлов.
import shutil

from dublib.Methods import CheckPythonMinimalVersion, MakeRootDirectories, ReadJSON

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)
# Создание папок в корневой директории.
MakeRootDirectories(["Uploads"])

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Чтение настроек.
Settings = ReadJSON("Settings.json")

# Если токен не указан, выбросить исключение.
if type(Settings["token"]) != str or Settings["token"].strip() == "":
    raise Exception("Invalid Telegram bot token.")

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ БОТА И ОБРАБОТКА КОМАНД <<<<< #
#==========================================================================================#

# Токен для работы определенного бота телегамм.
bot = telebot.TeleBot(Settings["token"])

# Создание переменной images - для подсчета изображений скачанных в последнем сообщении.
images = 0
# Создание переменной videos - для подсчета видео скачанных в последнем сообщении.
videos = 0

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
    

# Обработчик фото и видео (в будущем возможно добавление: 'document', 'audio').
@bot.message_handler(content_types=['photo', 'video'])
# Сохранение фото/видео.
def bot_message(message):
    # Создание глобальной переменной images.
    global images
    # Создание глобальной переменной videos.
    global videos
    # Вывод информации о загрузке файлов.
    bot.send_message(message.chat.id, 'Идет сборка коллекции')
    # Если тип получаемого контента - изображение:
    if message.content_type == 'photo':
        # Получение id изображения.
        photo_id = message.photo[-1].file_id 
        # Получение данных фотографии.
        file_info = bot.get_file(photo_id) 
        # Отпраляем запрос, для получения фото.
        file = requests.get(f'https://api.telegram.org/file/bot{Settings["token"]}/{file_info.file_path}') 
        # Даем название изображениям.
        file_name = 'photo' + message.photo[-1].file_id + '.jpg' 
        # Открываем файл фотографии.
        with open(f'Uploads/{file_name}', 'wb') as f:
            # Сохраняем изображение.
            f.write(file.content)
            # Осуществление подсчета скачанных в последнем сообщении изображений.
            images +=1
    else:
        # Получение id видео.
        video_id = message.video.file_id 
        # Получение данных фотографии.
        file_info = bot.get_file(video_id) 
        # Отпраляем запрос, для получения фото.
        file = requests.get(f'https://api.telegram.org/file/bot{Settings["token"]}/{file_info.file_path}') 
        # Даем название изображениям.
        file_name = 'video' + message.video.file_id + '.mp4' 
        # Открываем файл фотографии.
        with open(f'Uploads/{file_name}', 'wb') as f:
            # Сохраняем изображение.
            f.write(file.content)
            # Осуществление подсчета скачанных в последнем сообщении видеофайлов.
            videos +=1
    # Создание глобальной переменной number_files.
    global number_files
    # Создание глобальной переменной number_videos.
    global number_videos
    # Создание глобальной переменной number_images.
    global number_images
    # Количество изображений в папке.
    number_files = len(os.listdir('Uploads'))
    # Количество файлов с расширением .jpg в папке.
    number_images = len(fnmatch.filter(os.listdir('Uploads/'),'*.jpg'))
    # Количество файлов с расширением .mp4 в папке.
    number_videos = len(fnmatch.filter(os.listdir('Uploads/'),'*.mp4'))
    # Вывод информации об успешности операции и количестве добавленных фотографий и видеофайлов.
    bot.send_message(message.chat.id, f'Добавлено {images} изображений и {videos} видео.')
    # Вывод информации об успешности операции и количестве добавленных фотографий и видеофайлов в коллекцию.
    bot.send_message(message.chat.id, f'В коллекцию добавлено {number_files} медиафайлов. Из них {number_images} изображений и {number_videos} видеофайлов.')


# Обработчик текста.
@bot.message_handler(content_types=['text'])
# Функция, выводящая ответ бота в ответ на текст.
def bot_message(message):
    # Если вызвана текст '📦 Начать сбор коллекции':
    if message.text == '📦 Начать сбор коллекции':
        # Вывод кнопки ⛔️ Остановить сбор коллекции.
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('⛔️ Остановить сбор коллекции'))
        # Отправка ботом сообщения и отображение кнопки(⛔️ Остановить сбор коллекции).
        bot.send_message(message.chat.id, 'Пришлите мне сообщение с медиафайлами. Вы также можете остановить сбор коллекции и закончить работу бота.', reply_markup=markup1)
    else:
        # Создание глобальной переменной markup.
        global markup
        # Создание глобальной переменной number_files.
        global number_files
        # Создание глобальной переменной number_videos.
        global number_videos
        # Создание глобальной переменной number_images.
        global number_images
        # Отправка ботом сообщения и отображение кнопки(📦 Начать сбор коллекции).
        bot.send_message(message.chat.id, f'Формирование коллекции окончено. В коллекции находится {number_files} файлов. Из них {number_images} изображений и {number_videos} видео.', reply_markup=markup)
        # Сохранение коллекции в архив.
        shutil.make_archive('archive', 'zip', 'Uploads' )
   

# Запуск работы кода.
if __name__ == "__main__":
    # Опрос серверов Telegram на предмет новых сообщений.
    bot.polling(none_stop=True)