
#==========================================================================================#
# >>>>> ПОДКЛЮЧЕНИЕ БИБЛИОТЕК И МОДУЛЕЙ <<<<< #
#==========================================================================================#

from dublib.Methods import RemoveFolderContent, ReadJSON


import datetime
import logging
import telebot
import shutil
import os
        
#==========================================================================================#
# >>>>> ОТПРАВКА СТАТИСТИКИ <<<<< #
#==========================================================================================#

def GenerateStatistics(Bot: telebot.TeleBot, UserID: str, ChatID: int, SizeObject: any, FlowObject):
    # Текст сообщения.
    MessageText = "Я собрал для вас статистику по типам файлов в вашем архиве\.\n\n"

    # Список названий файлов в директории пользователя.
    Files = os.listdir("Data/Files/" + str(UserID))
    
    # Размер всех скачанных файлов.
    Size = SizeObject.GetSizeDirectory(Files, str(UserID))

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

    # Добавление статистики.
    MessageText += "⏳ _Количество файлов, которые загружаются_\: " + str(FlowObject.CountMessagesBufer()) + "\n" + "\n"
    MessageText += "⏳ _Типы файлов в вашем хранилище_\: " + "\n"
    MessageText += "📷 _Фото_\: " + str(FileTypes["photo"]) + "\n"
    MessageText += "📽 _Видео_\: " + str(FileTypes["video"]) + "\n"
    MessageText += "💼 _Документы_\: " + str(FileTypes["document"]) + "\n"
    MessageText += "🎵 _Аудио_\: " + str(FileTypes["audio"]) + "\n"
    try:
        MessageText += "❔📦 _Размер всех медиафайлов_\: " + str(SizeObject.Converter("Any", Size)).replace('.','\.') + "\n" + "\n"
    except:
        MessageText += "❔📦 _Размер всех медиафайлов_\: " + "0B" + "\n" + "\n"
    MessageText += "❔❌_Количество медиафайлов, доступных для скачивания только в Premium версии_\: "  + str(len(ReadJSON("Data/Users/" + UserID + ".json")["UnloadedFiles"]))
    
    # Отправка статистики.
    Bot.send_message(ChatID, MessageText, parse_mode = "MarkdownV2")

#==========================================================================================#
# >>>>> ОТПРАВКА АРХИВА  <<<<< #
#==========================================================================================#

def SendArchive(Bot: telebot.TeleBot, UserID: str, ChatID: int, UserDataObject: any ):

    # Получение текущей даты.
    Date = datetime.datetime.now()

    # Форматирование названия файла.
    Date = str(Date).replace(':', '-').split('.')[0]
    
    # Состояние: удалась ли отправка архива.
    IsSended = False

    # Если существуют файлы для архивации.
    while len(os.listdir("Data/Files/" + UserID)) > 0:

        # Архивирование файлов пользователя.
        shutil.make_archive(f"Data/Archives/{UserID}/{Date}", "zip", "Data/Files/" + UserID)

        # Логгирование.
        logging.info("Архив собран.")

        # Очистка файлов пользователя. 
        RemoveFolderContent("Data/Files/" + UserID)

        # Бинарное содержимое архива.
        BinaryArchive = None

        # Чтение архива.
        with open(f"Data/Archives/{UserID}/{Date}.zip", "rb") as FileReader:
            BinaryArchive = FileReader.read()
        
        # Отправка архива пользователю.
        Bot.send_document(ChatID, BinaryArchive, visible_file_name = f"{Date}.zip")

        # Логгирование.
        logging.info("Архив отправлен.")

        try: 
            # Получение списка словарей незагруженных файлов.
            UnloadedFiles = UserDataObject.GetInfo(UserID, "UnloadedFiles")

            # print(UnloadedFiles)
            # print(UnloadedFiles[0]["type"])
                
            if UnloadedFiles[0]["type"] == "document":
                # logging.info("Отправка документа началась.")   
                # Отправка файлов, которые невозможно скачать.
                Bot.send_document(ChatID, document = UnloadedFiles[0]["file"])

                # Логгирование.
                logging.info("Отправка документа удалась.")   

            if UnloadedFiles[0]["type"] == "audio":
                # logging.info("Отправка документа началась.")   
                # Отправка файлов, которые невозможно скачать.
                Bot.send_audio(ChatID, audio = UnloadedFiles[0]["file"])

                # Логгирование.
                logging.info("Отправка аудио удалась.")   

            if UnloadedFiles[0]["type"] == "video":
                # logging.info("Отправка документа началась.")   
                # Отправка файлов, которые невозможно скачать.
                Bot.send_video(ChatID, video = UnloadedFiles[0]["file"])

                # Логгирование.
                logging.info("Отправка видео удалась.")   

            if UnloadedFiles[0]["type"] == "photo":
                # logging.info("Отправка документа началась.")   
                # Отправка файлов, которые невозможно скачать.
                Bot.send_photo(ChatID, photo = UnloadedFiles[0]["file"])

                # Логгирование.
                logging.info("Отправка фото удалась.")   
             


        except:
            # Логгирование.
            logging.info("Отправка файла не удалась")
       
        # Очистка архивов пользователя. 
        RemoveFolderContent("Data/Archives/" + UserID)
        
        # Переключение состояния.
        IsSended = True

    return IsSended


