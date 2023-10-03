from dublib.Methods import RemoveFolderContent
from telebot import types

import datetime
import requests
import telebot
import shutil
import os

# Создаёт набор кнопок.
def CreateKeyboard(TextList: list[str], CallbackList: list[str]) -> types.InlineKeyboardMarkup:
	# Набор кнопок.
	Keyboard = types.InlineKeyboardMarkup()

	# Для каждого набора данных.
	for Index in range(0, len(TextList)):
		# Создание кнопки.
		Keyboard.add(types.InlineKeyboardButton(text = TextList[Index], callback_data = CallbackList[Index]))

	return Keyboard

# Загружает файл.
def DownloadFile(Bot: telebot.TeleBot, Settings: dict, FileID: int, UserID: str) -> bool:
	# Получение данных файла.
	FileInfo = Bot.get_file(FileID) 
	# Расширение файла.
	FileType = "." + FileInfo.file_path.split('.')[-1]

	# Загрузка файла.
	Response = requests.get("https://api.telegram.org/file/bot" + Settings["token"] + f"/{FileInfo.file_path}")

	# Сохранение файла.
	with open(f"Data/Files/{UserID}/" + str(FileID) + FileType, "wb") as FileWriter:
		FileWriter.write(Response.content)

# Отправляет пользователю статистику медиафайлов.
def GenerateStatistics(Bot: telebot.TeleBot, UserID: str, ChatID: int):
	# Текст сообщения.
	MessageText = "Я собрал для вас статистику по типам файлов в вашем архиве\.\n\n"
	# Список названий файлов в директории пользователя.
	Files = os.listdir("Data/Files/" + UserID)
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
	MessageText += "🎵 _Аудио_\: " + str(FileTypes["audio"])
	# Отправка статистики.
	Bot.send_message(ChatID, MessageText, parse_mode = "MarkdownV2")

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