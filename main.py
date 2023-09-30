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
# Создание переменной documents - для подсчета видео скачанных в последнем сообщении.
documents = 0
# Создание переменной documents - для подсчета видео скачанных в последнем сообщении.
audios = 0

# Создаем basic_keyboard для создания кнопок.
def CreateButtonArchivingCollectionMedia():
    # Создание InlineKeyboard.
    keyboard = types.InlineKeyboardMarkup()
    # Создание и добавление кнопки '⛔️ Остановить сбор коллекции' на клавиатуру.
    keyboard.add(types.InlineKeyboardButton(text='⛔️ Остановить сбор коллекции', callback_data='⛔️ Остановить сбор коллекции'))
    # Вывод клавиатуры.
    return keyboard

# Создаем basic_keyboard для создания кнопок.
def CreateButtonStartingCollectionMedia():
    # Создание InlineKeyboard.
    keyboard = types.InlineKeyboardMarkup()
    # Создание и добавление кнопки '📦 Начать сбор коллекции' на клавиатуру.
    keyboard.add(types.InlineKeyboardButton(text='📦 Начать сбор коллекции', callback_data='📦 Начать сбор коллекции'))
    # Вывод клавиатуры.
    return keyboard

# Обработчик команды start.
@bot.message_handler(commands=['start'])
# Функция, выводящая приветствие и кнопку для дальнейшей работы бота.
def start(message):
    # Вывод клавиатуры после нажатия ввода /start.
    keyboard = CreateButtonStartingCollectionMedia()
    bot.send_message(message.chat.id, 
                     'Здравствуйте! Я - бот, который облегчит вам сохранение фото и видео из сообщений.\nДля начала работы, нажмите на кнопку: 📦 Начать сбор коллекции.',
                       reply_markup = keyboard)
    # Отправка ботом вступительного сообщения и кнопочек.
    global process, resultlastmessage, allarchivedmessage, result
    process=bot.send_message(message.chat.id,'yy')
    resultlastmessage=bot.send_message(message.chat.id, 'tty')
    allarchivedmessage=bot.send_message(message.chat.id,'yttt')
    result=bot.send_message(message.chat.id,'t')




# Обработчик кнопок.
@bot.callback_query_handler(func=lambda call: True)
# Функция, выводящая ответ бота в ответ на текст.
def bot_message(call):
    # Если вызвана текст '📦 Начать сбор коллекции':
    if call.data == '📦 Начать сбор коллекции':
        # Вывод кнопки ⛔️ Остановить сбор коллекции.
        keyboard = CreateButtonArchivingCollectionMedia()
        # Отправка ботом сообщения и отображение кнопки(⛔️ Остановить сбор коллекции).
        bot.send_message(call.message.chat.id, 'Пришлите мне сообщение с медиафайлами. Вы также можете остановить сбор коллекции и закончить работу бота.', reply_markup=keyboard)
    else:
        # Вывод клавиатуры после нажатия ввода /start.
        keyboard = CreateButtonStartingCollectionMedia()
         # Создание глобальной переменной number_files.
        global number_files
        # Создание глобальной переменной number_videos.
        global number_videos
         # Создание глобальной переменной number_images.
        global number_images
        # Сохранение коллекции в архив.
        shutil.make_archive('archive', 'zip', 'Uploads' )
        # Открытие архива в виде файла.
        archive = open('archive.zip',"rb")
        # Отправка заархивированного файла пользователю.
        bot.send_document(call.message.chat.id, archive)
        # Отправка ботом сообщения и отображение кнопки(📦 Начать сбор коллекции).
        result = str('Формирование коллекции окончено.\n')
        if number_images >=1:
            result += 'Фото: ' + str(number_images)
        if number_videos >=1:
            result += 'Видео: ' + str(number_images)
        if number_files >=1:
            result += 'Всего файлов: ' + str(number_images)
        bot.send_message(call.message.chat.id, result, reply_markup=keyboard)


# Обработчик фото, видео, аудио, документов.
@bot.message_handler(content_types=['photo', 'video', 'audio', 'document'])
# Сохранение фото/видео.
def bot_message(message):
    global process, resultlastmessage, allarchivedmessage, result
    # Создание глобальной переменной images.
    global images
    # Создание глобальной переменной videos.
    global videos
    # Создание глобальной переменной documents.
    global documents
    # Создание глобальной переменной audios.
    global audios
    # Вывод информации о загрузке файлов.
    try:
        bot.delete_message(message.chat.id, process.message_id)
    except Exception:
        pass
    process = bot.send_message(message.chat.id, f'Идет сборка коллекции')
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
    elif message.content_type == 'video':
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
    elif message.content_type == 'document':
        # Получение id видео.
        document_id = message.document.file_id 
        # Получение данных фотографии.
        file_info = bot.get_file(document_id) 
        # Отпраляем запрос, для получения фото.
        file = requests.get(f'https://api.telegram.org/file/bot{Settings["token"]}/{file_info.file_path}') 
        # Даем название изображениям.
        file_name = message.document.file_name 
        # Открываем файл фотографии.
        with open(f'Uploads/{file_name}', 'wb') as f:
            # Сохраняем изображение.
            f.write(file.content)
            # Осуществление подсчета скачанных в последнем сообщении видеофайлов.
            documents +=1
    elif message.content_type == 'audio':
        # Получение id видео.
        audio_id = message.audio.file_id 
        # Получение данных фотографии.
        file_info = bot.get_file(audio_id) 
        # Отпраляем запрос, для получения фото.
        file = requests.get(f'https://api.telegram.org/file/bot{Settings["token"]}/{file_info.file_path}') 
        # Даем название изображениям.
        file_name = message.audio.file_name 
        # Открываем файл фотографии.
        with open(f'Uploads/{file_name}', 'wb') as f:
            # Сохраняем изображение.
            f.write(file.content)
            # Осуществление подсчета скачанных в последнем сообщении видеофайлов.
            audios +=1
    else: 
        print('potom')
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
    try:
        bot.delete_message(message.chat.id, resultlastmessage.message_id)
    except Exception:
        pass
    # Вывод информации об успешности операции и количестве добавленных фотографий и видеофайлов.
    resultlastmessage = bot.send_message(message.chat.id, f'Добавлено {images} изображений и {videos} видео.')
    try:
        bot.delete_message(message.chat.id, allarchivedmessage.message_id)
    except Exception:
        pass
    # Вывод информации об успешности операции и количестве добавленных фотографий и видеофайлов в коллекцию.
    allarchivedmessage = bot.send_message(message.chat.id, f'В коллекцию добавлено {number_files} медиафайлов. Из них {number_images} изображений и {number_videos} видеофайлов.')
    try:
        bot.delete_message(message.chat.id, result.message_id)
    except Exception:
        pass
    # Вывод кнопки ⛔️ Остановить сбор коллекции.
    keyboard = CreateButtonArchivingCollectionMedia()
    # Отправка ботом сообщения и отображение кнопки(⛔️ Остановить сбор коллекции).
    result = bot.send_message(message.chat.id, 'Пришлите мне сообщение с медиафайлами. Вы также можете остановить сбор коллекции и закончить работу бота.', reply_markup=keyboard)
    

# Обработчик текста.
@bot.message_handler(content_types=['text'])
def Exeptions(message):
   pass
     

# Запуск работы кода.
if __name__ == "__main__":
    # Опрос серверов Telegram на предмет новых сообщений.
    bot.polling(none_stop=True)