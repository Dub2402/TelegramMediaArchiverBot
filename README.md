# Telegram Media Archiver Bot
**Telegram Media Archiver Bot** – это [Telegram](https://telegram.org) - бот  для автоматической архивации медиавложений из ваших сообщений. С его помощью вы легко сможете скачать сотни файлов одним нажатием кнопки.

## Порядок установки и использования
1. Загрузить репозиторий. Распаковать.

2. Установить [Python](https://www.python.org/downloads/) версии 3.11 и выше. Рекомендуется добавить в PATH.

3. Открыть каталог со скриптом в консоли: можно воспользоваться командой cd или встроенными возможностями файлового менеджера.

4. Создать виртуальное окружение Python.

```
python -m venv .venv
```

5. Активировать вирутальное окружение.

#### Для Windows.
    
```shell
.venv\Scripts\activate.bat
```

#### Для Linux или MacOS.

```bash
source .venv/bin/activate
```

6. Установить зависимости скрипта.

```
pip install -r requirements.txt
```

7. Настроить бота путём редактирования _Settings.json_.

### Settings.json.

```JSON
"token": ""
```

Токен бота Telegram (можно получить у [BotFather](https://t.me/BotFather)).

8. Для удобства работы с ботом рекомендуется добавить список команд в настройках бота в [BotFather](https://t.me/BotFather).

Start - start working.

Сlear - reset the archive build.

Statistics - send file statistics.

Archive - archive files and send it.

9. Запустить файл _main.py_.

```
python main.py
```

10. Для автоматического запуска рекомендуется провести инициализацию сервиса через [systemd](systemd/README.md) на Linux или путём добавления его в автозагрузку на Windows.

11. Перейти в чат с ботом, токен которого указан в настройках, и следовать его инструкциям.


---
**_Copyright © Dub Irina. 2023-2025._**


