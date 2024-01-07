
#==========================================================================================#
# >>>>> ПОДКЛЮЧЕНИЕ БИБЛИОТЕК И МОДУЛЕЙ <<<<< #
#==========================================================================================#

from dublib.Methods import RemoveFolderContent, ReadJSON

import logging
import datetime
import os
import requests
import shutil
import telebot

#==========================================================================================#
# >>>>> ЗАГРУЗКА ОЧЕРЕДИ ИЗ МЕДИАФАЙЛОВ <<<<< #
#==========================================================================================#

# Загружает файл.
def DownloadFile(MessagesBufer, Settings, UserDataObject):
    # Получение данных файла.
    try:
        # Расширение файла.
        FileType = "." + MessagesBufer[0].file_path.split('.')[-1]

        # Загрузка файла.
        Response = requests.get("https://api.telegram.org/file/bot" + Settings["token"] + f"/{ MessagesBufer[0].file_path}")
        
        # Сохранение файла.
        with open(f"Data/Files/{UserDataObject.getUserID()}/" + str(MessagesBufer[0].file_unique_id) + FileType, "wb") as FileWriter:
            FileWriter.write(Response.content)
            UpdatingSize = (ReadJSON("Data/Users/" + UserDataObject.getUserID() + ".json")["Size"]) + MessagesBufer[0].file_size/1024
            logging.info(f"Файл загружен: {UpdatingSize}.")
            UserDataObject.__UpdateSizeUser(UpdatingSize)
            logging.info("Переданы данные файлов.")
            # Удаление элемента из списка.
            MessagesBufer.remove(MessagesBufer[0])
            
    except: 
        print(0)
        
#==========================================================================================#
# >>>>> ОТПРАВКА СТАТИСТИКИ <<<<< #
#==========================================================================================#

# Отправляет пользователю статистику медиафайлов.
def GenerateStatistics(Bot: telebot.TeleBot, UserID: str, ChatID: int, SizeDirectory):
    # Текст сообщения.
    MessageText = "Я собрал для вас статистику по типам файлов в вашем архиве\.\n\n"

    # Список названий файлов в директории пользователя.
    Files = os.listdir("Data/Files/" + UserID)
    Size =  SizeDirectory(f'Data/Files/{UserID}')                                                                          

    # Словарь типов файлов.
    FileTypes = {
        "photo": 0,
        "video": 0,
        "document": 0,
        "audio": 0
    }

    # Словарь расширений файлов.
    FileExtensions = {
        "photo": ["jpg", "png", "webp", "jpeg", "ico", "gif", "svg"],
        "video": ["mp4", "avi", "wmw", "mkv", "3gp", "flv", "mov", "mpeg"],
        "audio": ["mp3", "ogg", "wav", "wma"]
    }
    
    # Для каждого файла.
    for File in Files:
        # Состояние: был ли типизирован файл.
        IsTyped = False

        # Для каждого типа расширений.
        for ExtensionType in FileExtensions.keys():
            # Расширение файла.
            FileExtension = File.split('.')[-1]
            
            # Если расширение файла принадлежит какому-то типу.
            if FileExtension in FileExtensions[ExtensionType]:
                # Инкремент количества файлов типа.
                FileTypes[ExtensionType] +=1
                # Переключение состояния типизации.
                IsTyped = True

        # Если тип не определён, то провести инкремент количества документов.
        if IsTyped == False:
            FileTypes["document"] +=1

    # Добавление счётчиков.
    MessageText += "📷 _Фото_\: " + str(FileTypes["photo"]) + "\n"
    MessageText += "📽 _Видео_\: " + str(FileTypes["video"]) + "\n"
    MessageText += "💼 _Документы_\: " + str(FileTypes["document"]) + "\n"
    MessageText += "🎵 _Аудио_\: " + str(FileTypes["audio"]) + "\n"
    MessageText += "❔📦_Размер всех медиафайлов_\: " + str(Size).replace('.','\.')

    # Отправка статистики.
    Bot.send_message(ChatID, MessageText, parse_mode = "MarkdownV2")

#==========================================================================================#
# >>>>> ОТПРАВКА АРХИВА  <<<<< #
#==========================================================================================#

# Архивирует файлы пользователя и отправляет в чат.
def SendArchive(Bot: telebot.TeleBot, UserID: str, ChatID: int) -> bool:

    # Получение текущей даты.
    Date = datetime.datetime.now()

    # Форматирование названия файла.
    Date = str(Date).replace(':', '-').split('.')[0]
    
    # Состояние: удалась ли отправка архива.
    IsSended = False

    # Если существуют файлы для архивации.
    if len(os.listdir("Data/Files/" + UserID)) > 0:
        # Архивирование файлов пользователя.
        shutil.make_archive(f"Data/Archives/{UserID}/{Date}", "zip", "Data/Files/" + UserID)

        # Очистка файлов пользователя. 
        RemoveFolderContent("Data/Files/" + UserID)

        # Бинарное содержимое архива.
        BinaryArchive = None

        # Чтение архива.
        with open(f"Data/Archives/{UserID}/{Date}.zip", "rb") as FileReader:
            BinaryArchive = FileReader.read()

        # Отправка архива пользователю.
        Bot.send_document(ChatID, BinaryArchive, visible_file_name = f"{Date}.zip")

        # Очистка архивов пользователя. 
        RemoveFolderContent("Data/Archives/" + UserID)
        
        # Переключение состояния.
        IsSended = True

    return IsSended

