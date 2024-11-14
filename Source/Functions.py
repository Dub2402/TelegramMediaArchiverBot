
#==========================================================================================#
# >>>>> ПОДКЛЮЧЕНИЕ БИБЛИОТЕК И МОДУЛЕЙ <<<<< #
#==========================================================================================#

from telebot.types import InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo
from dublib.Methods.Filesystem import RemoveDirectoryContent
from Source.Users import UsersManager
from .MessageBox import MessageBox
from telebot import types

import datetime
import logging
import telebot
import zipfile
import os

#==========================================================================================#
# >>>>> ОТПРАВКА СТАТИСТИКИ <<<<< #
#==========================================================================================#

def GenerateStatistics(Bot: telebot.TeleBot, UserID: str, ChatID: int, SizeObject: any, FlowObject, UsersManagerObject):
	# Создание объекта класса MessageBox.
	MessageBoxObject = MessageBox(Bot = Bot)

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
	count = FlowObject.CountMessagesBufer()
	size = SizeObject.Converter("Any", Size)
	photo = FileTypes["photo"]
	video = FileTypes["video"]
	documents = FileTypes["document"]
	audio = FileTypes["audio"]
	mistakes = len(UsersManagerObject.get_user(UserID).unloaded_files)
	
	# Отправка статистики.
	MessageBoxObject.send(ChatID, "statistic", "statistic", {"count": count, "size": size, "photo": photo, "video": video, "documents": documents, "audio": audio, "mistakes": mistakes})
	
#==========================================================================================#
# >>>>> ОТПРАВКА АРХИВА  <<<<< #
#==========================================================================================#

def SendArchive(Bot: telebot.TeleBot, UserID: str, ChatID: int, UsersManagerObject: UsersManager):
	# Создание объекта класса MessageBox.
	MessageBoxObject = MessageBox(Bot = Bot)

	# Получение текущей даты.
	Date = datetime.datetime.now()

	# Форматирование названия файла.
	Date = str(Date).replace(':', '-').split('.')[0]
	
	# Состояние: удалась ли отправка архива.
	Status = False

	# Если существуют файлы для архивации.
	while len(os.listdir("Data/Files/" + str(UserID))) > 0:

		# Отправка сообщений пользователю.
		MessageBoxObject.send(ChatID, "archiving", "waiting")
		
		# Создание нового архива.
		Archieve = zipfile.ZipFile(f'Data/Archives/{UserID}/{Date}.zip', 'w', compression = zipfile.ZIP_DEFLATED, compresslevel = 9)
	
		for file in os.listdir(f'Data/Files/{UserID}'): 
			# Создание относительных путей и запись файлов в архив.
			Archieve.write(filename = f'Data/Files/{UserID}/{file}', arcname = file)

		# Закрытие архива.
		Archieve.close()
		# Очистка файлов пользователя. 
		RemoveDirectoryContent("Data/Files/" + str(UserID))

		# Бинарное содержимое архива.
		BinaryArchive = None
		
		# Чтение архива.
		with open(f"Data/Archives/{UserID}/{Date}.zip", "rb") as FileReader:
			BinaryArchive = FileReader.read()
		
		try:
			# Отправка архива пользователю.
			Bot.send_document(ChatID, BinaryArchive, visible_file_name = f"{Date}.zip")

			# Логгирование.
			logging.info("Архив отправлен.")

			try: 
				# Получение списка словарей незагруженных файлов.
				UnloadedFiles = UsersManagerObject.get_user(UserID).unloaded_files

				# Получение длины списка словарей незагруженных файлов.
				Lenth = len(UnloadedFiles)
				
				Media = list()

				if Lenth > 0:
					# Отправка сообщения.
					MessageBoxObject.send(ChatID, "mistakes", "waiting")
					for Sequence in range(Lenth):
						if UnloadedFiles[Sequence]["type"] == "video":
							Media.append(InputMediaVideo(media = UnloadedFiles[Sequence]["idfile"]))
					
						if UnloadedFiles[Sequence]["type"] == "document": 
							Media.append(InputMediaDocument(media = UnloadedFiles[Sequence]["idfile"]))
					
						if UnloadedFiles[Sequence]["type"] == "audio": 
							Media.append(InputMediaAudio(media = UnloadedFiles[Sequence]["idfile"]))

						if UnloadedFiles[Sequence]["type"] == "photo": 
							Media.append(InputMediaPhoto(media = UnloadedFiles[Sequence]["idfile"]))
					
					# Удаление словаря ошибок отправленного файла.
					Bot.send_media_group(ChatID, Media)
					
					# Удаление всех ошибочных файлов из json.
					UsersManagerObject.set_user_value(UserID, "UnloadedFiles", [])  
			
			except Exception as ExceptionData:
				# Логгирование.
				logging.info(f"Отправка файла не удалась. {ExceptionData}")
		
			# Очистка архивов пользователя. 
			RemoveDirectoryContent("Data/Archives/" + str(UserID))
			
			# Переключение состояния.
			Status = True

		except Exception as ExceptionData:
			# Логгирование.
			logging.info(f"Отправка архива не удалась. {ExceptionData}")

			# Отправка сообщения.
			MessageBoxObject.send(UserID, "errorsending", "error" )
			
			# Переключение состояния.
			Status = True

	return Status


