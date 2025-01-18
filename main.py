from dublib.Methods.Filesystem import MakeRootDirectories, RemoveDirectoryContent
from dublib.Methods.System import CheckPythonMinimalVersion
from dublib.Methods.Filesystem import ReadJSON
from dublib.Methods.System import Clear

from Source.Functions import GenerateStatistics, SendArchive
from Source.Users import UsersManager
from Source.MessageBox import MessageBox
from Source.Sizer import Sizer
from Source.Flow import Flow

from telebot import types
import logging
import telebot

Clear()

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ СКРИПТА <<<<< #
#==========================================================================================#

# Проверка поддержки используемой версии Python.
CheckPythonMinimalVersion(3, 10)

# Создание папки в корневой директории.
MakeRootDirectories(["Data/Files", "Data/Archives", "Data/Users"])

#==========================================================================================#
# >>>>> НАСТРОЙКА ЛОГИРОВАНИЯ <<<<< #
#==========================================================================================#

# Создание настроек логирования.
logging.basicConfig(level=logging.INFO, encoding="utf-8", filename="LOGING.log", filemode="w",
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Чтение настроек.
Settings = ReadJSON("Settings.json")

# Если токен не указан, выбросить исключение.
if type(Settings["token"]) != str or Settings["token"].strip() == "":
    raise Exception("Invalid Telegram bot token.")

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ БОТА <<<<< #
#==========================================================================================#

# Токен для работы определенного бота телегамм.
Bot = telebot.TeleBot(Settings["token"])

#==========================================================================================#
# >>>>> СОЗДАНИЕ ОБЪЕКТОВ <<<<< #
#==========================================================================================#

# Создание объекта класса Flow.
FlowObject = Flow(Settings)

# Создание объекта класса Sizer.
SizerObject = Sizer()

# Создание объекта класса MessageBox.
MessageBoxObject = MessageBox(Bot = Bot)

#Создание объекта класса UsersManager.
UsersManagerObject = UsersManager()

#==========================================================================================#
# >>>>> ОБРАБОТКА КОМАНДЫ ARCHIVE <<<<< #
#==========================================================================================#

@Bot.message_handler(commands=["archive"])
def ProcessCommandArchive(Message: types.Message):
    # Авторизация пользователя.
    UsersManagerObject.auth(Message.from_user)
    
    # Если очередь отправки файлов пуста.
    if FlowObject.EmptyFlowStatus() == True:
        # Если не удалась отправка архива.
        if SendArchive(Bot, Message.from_user.id, Message.chat.id, UsersManagerObject) == False:
            # Отправка сообщения: пользователь не отправил ни одного файла.
            MessageBoxObject.send(Message.chat.id, "no-files", "error")

    else:
        # Отправить инструкции пользователю.
        MessageBoxObject.send(Message.chat.id, "expectation", "waiting", {"reason": "Идёт загрузка файлов\\."})

#==========================================================================================#
# >>>>> ОБРАБОТКА КОМАНДЫ ClEAR <<<<< #
#==========================================================================================#

@Bot.message_handler(commands=["clear"])
def ProcessCommandClear(Message: types.Message):
    # Авторизация пользователя.
    UsersManagerObject.auth(Message.from_user)

    # Есть ли файлы пользователя в потоке.
    if FlowObject.CheckUserFilesPresence(Message.from_user.id) == False:
        # Удаление файлов пользователя.
        RemoveDirectoryContent("Data/Files/" +str(Message.from_user.id))

        # Удаление незагруженных файлов в json.
        UsersManagerObject.set_user_value(Message.from_user.id, "UnloadedFiles", [])

        # Отправка сообщения.
        MessageBoxObject.send(Message.chat.id, "wellclear", "done")

    else:
        # Отправка сообщения.
        MessageBoxObject.send(Message.chat.id, "expectation", "waiting", {'reason': 'Не все ваши файлы загружены\\.'})

#==========================================================================================#
# >>>>> ОБРАБОТКА КОМАНДЫ START <<<<< #
#==========================================================================================#

@Bot.message_handler(commands=["start"])
def ProcessCommandStart(Message: types.Message):
    # Авторизация пользователя.
    UsersManagerObject.auth(Message.from_user)

    # Отправка приветствия.
    MessageBoxObject.send(Message.chat.id, "greeting", "info")
    

#=========================================================================================#
# >>>>> ОБРАБОТКА КОМАНДЫ STATISTICS <<<<< #
#==========================================================================================#

@Bot.message_handler(commands=["statistics"])
def ProcessCommandStatistics(Message: types.Message):
    # Авторизация пользователя.
    UsersManagerObject.auth(Message.from_user)

    # Отправка статистики медиафайлов.
    GenerateStatistics(Bot, Message.from_user.id, Message.chat.id, SizerObject, FlowObject, UsersManagerObject)

#=========================================================================================#
# >>>>> ОБРАБОТЧИК МЕДИАФАЙЛОВ <<<<< #
#==========================================================================================#

@Bot.message_handler(content_types=["photo", "video", "audio", "document"])
def ProcessFileUpload(Message: types.Message):
    # Авторизация пользователя.
    UsersManagerObject.auth(Message.from_user)
    
    # ID файла.
    FileID = None

    # UniqueID файла.
    UniqueID = None

    # Если тип файла – фото.
    if Message.content_type == "photo":
        FileID = Message.photo[-1].file_id
        UniqueID = Message.photo[-1].file_unique_id

    # Если тип файла – видео.
    elif Message.content_type == "video":
        FileID = Message.video.file_id
        UniqueID = Message.video.file_unique_id

    # Если тип файла – аудио.
    elif Message.content_type == "audio":
        FileID = Message.audio.file_id
        UniqueID = Message.audio.file_unique_id

    # Если тип файла – документ.
    elif Message.content_type == "document":
        FileID = Message.document.file_id
        UniqueID = Message.document.file_unique_id
 
    try:
        # Получение данных файла. 
        FileInfo = Bot.get_file(FileID)

        # Логгирование.
        logging.info("Получены данные файла.")
        
        # Если размер файла меньше 20 MB.
        if SizerObject.CheckSize(FileInfo) == True:

            # # Размер всех файлов, которые будут скачаны.
            # UpdatingSize = UsersManagerObject.get_user(Message.from_user.id).size + SizerObject.Converter("KB", FileInfo.file_size)

                        
            # Условие проверки лимита пользователя (неактивно: UpdatingSize < 20480:).
            if True:
                # Запись в json.
                UsersManagerObject.add_size(Message.from_user.id, SizerObject.Converter("KB", FileInfo.file_size))
                # Добавление файла в очередь.
                FlowObject.AddFileInfo(FileInfo, Message.from_user.id)

                logging.info("Файл добавлен в очередь.")
    
            # else:
            #     # Добавление незагруженных файлов.
            #     UsersManagerObject.add_unloaded_file(Message.from_user.id, FileID, UniqueID, Message.content_type)

    except: 
        UnploadedFiles = UsersManagerObject.get_user(Message.from_user.id).unloaded_files 

        if UnploadedFiles == []:
            # Добавление незагруженных файлов.
            UsersManagerObject.add_unloaded_file(Message.from_user.id, FileID, UniqueID, Message.content_type)
        else:
            for i in UnploadedFiles:
                if i["uniqueidfile"] == UniqueID:
                    logging.info ("Такой фaйл уже есть в незагруженных файлах.")

                else:
                    # Добавление незагруженных файлов.
                    UsersManagerObject.add_unloaded_file(Message.from_user.id, FileID, UniqueID, Message.content_type)

# Запуск обработки запросов Telegram.
Bot.infinity_polling()