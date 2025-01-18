from dublib.Methods.Filesystem import ReadJSON
from telebot import TeleBot

class MessageBox:
	"""
	Контейнер сообщений Telegram.
	"""

	def __PutData(self, Message: str, Data: dict) -> str:
		"""
		Подставляет на выделенные места данные.
			Message – текст сообщения со слотами для подстановки;
			Data – словарь подстанавливаемых значений.
		"""

		# Для каждого параметра.
		for Key in Data.keys():
			# Слот.
			Slot = "{" + str(Key) + "}"
			
			# Если сообщение содержит слот.
			if Slot in Message:
				# Выполнение подстановки.
				Message = Message.replace(Slot, str(Data[Key]))

		return Message

	def __init__(self, path: str = "Source/Messages.json", Bot: TeleBot | None = None):
		"""
		Контейнер сообщений Telegram.
			path – путь к файлу с сообщениями.
		"""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Данные сообщений.
		self.__Data = ReadJSON(path)
		# Экземпляр бота.
		self.__Bot = Bot

	def get(self, key: str, header: str | None = None, data: dict | None = None) -> str:
		"""
		Возвращает текст сообщения.
			key – ключ для получения текста из описательного файла;
			header – идентификатор заголовка;
			data – словарь подстанавливаемых значений.
		"""

		# Текст сообщения.
		Message = self.__Data["messages"][key]
		# Если указан заголовок, добавить его.
		if header != None: Message = self.__Data["headers"][header] + "\n\n" + Message
		# Если переданы данные для подстановки, подставить.
		if data != None: Message = self.__PutData(Message, data)

		return Message

	def send(self, target: int | str, key: str, header: str | None = None, data: dict | None = None):
		"""
		Отправляет сообщение в чат.
			target – ID пользователя или чата;
			key – ключ для получения текста из описательного файла;
			header – идентификатор заголовка;
			data – словарь подстанавливаемых значений.
		"""

		# Если бот инициализирован.
		if self.__Bot != None:
			# Отправка сообщения.
			self.__Bot.send_message(
				chat_id = target,
				text = self.get(key, header, data),
				parse_mode = "MarkdownV2",
				disable_web_page_preview = True
			)

		else:
			# Выброс исключения.
			raise Exception("Bot not initialized into MessageBox object.")