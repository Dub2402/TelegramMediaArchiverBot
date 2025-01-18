from dublib.Methods.Filesystem import ReadJSON, WriteJSON

import telebot
import os

class UserData:
	"""Объектное представление пользователя."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#
	
	@property
	def id(self) -> int:
		"""ID пользователя."""

		return self.__UserID

	@property
	def is_premium(self) -> bool:
		"""Premium статус пользователя."""

		return self.__IsPremium

	@property
	def size(self) -> int:
		"""Premium статус пользователя."""

		return self.__Size

	@property
	def unloaded_files(self) -> list:
		"""Список файлов, при загрузке которых возникла ошибка."""

		return self.__UnloadedFiles

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, user_id: int, data: dict):
		"""Объектное представление пользователя."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# ID пользователя.
		self.__UserID = user_id
		# Состояние: есть ли Premium у пользователя.
		self.__IsPremium = data["Premium"]
		# Размер загруженных пользователем данных.
		self.__Size = data["Size"]
		# Размер загруженных пользователем данных.
		self.__UnloadedFiles = data["UnloadedFiles"]

class UsersManager:
	"""Менеджер пользователей."""

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckErrorPrescense(self, UserID: int, UniquieID: str) -> bool:
		"""Проверяет наличие уже описанной ошибки загрузки файла."""
		# Список ошибок.
		Errors = self.get_user(UserID).unloaded_files
		# Список уникальных ID незагруженных файлов.
		ErrorsUniquieID = list()
		# Для каждой ошибки записать уникальный ID.
		for Error in Errors: ErrorsUniquieID.append(Error["uniqueidfile"])
		# Результат проверки.
		IsPrescense = False
		# Если ошибка уже описана, переключить статус.
		if UniquieID in ErrorsUniquieID: IsPrescense = True

		return IsPrescense

	def __CreateUser(self, UserID: int, Premium: bool) -> UserData:
		"""Создаёт пользователя."""

		# Запись пользовательских данных.
		self.__Users[UserID] = {
			"Size": 0,
			"Premium": Premium,
			"UnloadedFiles": list()
		}
		# Создание папок пользователей.
		if os.path.exists(f"Data/Files/{UserID}") == False: os.makedirs(f"Data/Files/{UserID}")
		if os.path.exists(f"Data/Archives/{UserID}") == False: os.makedirs(f"Data/Archives/{UserID}")
		# Сохранение файла.
		self.__SaveUser(UserID)

		return UserData(UserID, self.__Users[UserID])

	def __LoadUsers(self):
		"""Загружает данные пользователей."""

		# Получение списка файлов в директории пользователей.
		Files = os.listdir("Data/Users")
		# Фильтрация только файлов формата JSON.
		Files = list(filter(lambda List: List.endswith(".json"), Files))

		# Для каждого файла.
		for File in Files:
			# Чтение файла.
			Bufer = ReadJSON(f"Data/Users/{File}")
			# ID пользователя.
			UserID = int(File.replace(".json", ""))
			# Запись пользовательских данных.
			self.__Users[UserID] = Bufer

	def __SaveUser(self, UserID: int):
		"""Сохраняет файл пользователя."""
		
		# Сохранение файла.
		WriteJSON(f"Data/Users/{UserID}.json", self.__Users[UserID])

	def __init__(self):
		"""Менеджер пользователей."""

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Словарь пользователей.
		self.__Users = dict()

		# Загрузка данных пользователей.
		self.__LoadUsers()

	def auth(self, user: telebot.types.User) -> UserData:
		"""
		Выполняет идентификацию пользователя. Возвращает объектное представление данных пользователя.
			user – данные пользователя.
		"""

		# Пользователь.
		User = self.get_user(user.id)

		# Если пользователь не идентифицирован.
		if User == None:
			# Создание нового пользователя.
			User = self.__CreateUser(user.id, user.is_premium)

		else:
			# Обновление Premium-статуса пользователя.
			self.set_user_value(user.id, "Premium", user.is_premium)

		return User

	def get_user(self, user_id: int | str) -> UserData | None:
		"""
		Возвращает объект данных пользователя.
			user_id – ID пользователя.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Пользователь.
		User = None
		# Если пользователь уже зарегестрирован в системе, записать его данные.
		if user_id in self.__Users.keys(): User = UserData(user_id, self.__Users[user_id])
		
		return User

	def get_user_data(self, user_id: int | str) -> dict | None:
		"""
		Возвращает словарь данных пользователя.
			user_id – ID пользователя.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Пользователь.
		User = None
		# Если пользователь уже зарегистрирован в системе, записать его данные.
		if user_id in self.__Users.keys(): User = self.__Users[user_id]

		return User

	def set_user_value(self, user_id: int | str, key: str, value: any) -> bool:
		"""
		Устанавливает новое значение для параметра пользователя.
			user_id – ID пользователя;
			key – ключ в словаре данных пользователя;
			value – значение ключа.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = False

		# Если пользователь идентифицирован.
		if user_id in self.__Users.keys():

			# Если ключ существует.
			if key in self.__Users[user_id].keys():
				# Перезапись данных пользователя.
				self.__Users[user_id][key] = value
				# Сохранение файла.
				self.__SaveUser(user_id)
				# Состояние: успешно ли обновление.
				IsSuccess = True

			else:
				# Выброс исключения.
				raise KeyError(f"Unknown key \"{key}\" in user data dictionary.")

		return IsSuccess

	def update_user_data(self, user_id: int | str, data: dict) -> bool:
		"""
		Полностью перезаписывает данные пользователя. Возвращает False при ошибке идентификации пользователя.
			user_id – ID пользователя;
			data – словарь данных пользователя.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = True

		# Если передан словарь и пользователь идентифицирован.
		if type(data) == dict and user_id in self.__Users.keys():
			# Перезапись данных пользователя.
			self.__Users[user_id] = data
			# Сохранение файла.
			self.__SaveUser(user_id)

		elif type(data) != dict:
			# Переключение состояния.
			IsSuccess = False
			# Выброс исключения.
			raise TypeError("Expected dict() type of data.")

		else:
			# Переключение состояния.
			IsSuccess = False

		return IsSuccess

	def remove_user(self, user_id: int | str) -> bool:
		"""
		Удаляет пользователя из системы.
			user_id – ID пользователя.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = False

		# Если пользователь идентифицирован.
		if user_id in self.__Users.keys():
			# Удаление пользователя.
			del self.__Users[user_id]
			# Удаление файлов и директорий пользователя.
			if os.path.exists(f"Data/Users/{user_id}.json") == True: os.remove(f"Data/Users/{user_id}.json")
			if os.path.exists(f"Data/Files/{user_id}") == True: os.rmdir(f"Data/Files/{user_id}")
			if os.path.exists(f"Data/Archives/{user_id}") == True: os.rmdir(f"Data/Files/{user_id}")
			# Переключение состояния.
			IsSuccess = True

		return IsSuccess

	#==========================================================================================#
	# >>>>> ЧАСТНЫЕ МЕТОДЫ УПРАВЛЕНИЯ ДАННЫМИ ПОЛЬЗОВАТЕЛЯ <<<<< #
	#==========================================================================================#

	def add_size(self, user_id: int | str, size: float | int) -> bool:
		"""
		Прибавляет размер файла в параметры пользователя.
			user_id – ID пользователя;
			size – размер файла в килобайтах.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = False

		# Если пользователь идентифицирован.
		if user_id in self.__Users.keys():
			# Прибавление размера загруженных файлов.
			self.__Users[user_id]["Size"] += int(size)
			# Сохранение файла.
			self.__SaveUser(user_id)
			# Переключение состояния.
			IsSuccess = True

		return IsSuccess

	def add_unloaded_file(self, user_id: int | str, file_id: str, unique_file_id: str, content_type: str) -> bool:
		"""
		Добавляет информацию о незагруженном файле в параметры пользователя.
			user_id – ID пользователя;
			file_id – ID файла;
			unique_file_id – уникальный ID файла;
			content_type – тип файла.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = False

		# Если пользователь идентифицирован.
		if user_id in self.__Users.keys():
			# Буфер описания.
			Bufer = {
				"userid": user_id,
				"idfile": file_id,
				"uniqueidfile": unique_file_id,
				"type": content_type
			}
			# Добавление данных о незагруженном файле.
			if self.__CheckErrorPrescense(user_id, unique_file_id) == False: self.__Users[user_id]["UnloadedFiles"].append(Bufer)
			# Сохранение файла.
			self.__SaveUser(user_id)
			# Переключение состояния.
			IsSuccess = True

		return IsSuccess

	def remove_unloaded_file(self, user_id: int | str, unique_file_id: str) -> bool:
		"""
		Удаляет информацию о незагруженном файле из параметров пользователя.
			user_id – ID пользователя;
			unique_file_id – уникальный ID файла.
		"""

		# Приведение ID пользователя к целочисленному.
		user_id = int(user_id)
		# Состояние: успешно ли обновление.
		IsSuccess = False

		# Если пользователь идентифицирован.
		if user_id in self.__Users.keys():

			# Для каждого незагруженного файла.
			for Index in range(0, len(self.__Users[user_id]["UnloadedFiles"])):

				# Если надйен файл с соответствующим уникальным ID.
				if unique_file_id == self.__Users[user_id]["UnloadedFiles"][Index]["uniqueidfile"]:
					# Удаление записи об ошибке.
					self.__Users[user_id]["UnloadedFiles"].pop(Index)
					# Сохранение файла.
					self.__SaveUser(user_id)
					# Переключение состояния.
					IsSuccess = True
					# Прерывание цикла.
					break

		return IsSuccess