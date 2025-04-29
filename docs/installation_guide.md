# Руководство по установке и запуску бота в Ubuntu ʕ •ᴥ•ʔ

## Подготовка системы

1. Убедитесь, что у вас установлен Python 3.8 или выше:
```bash
python3 --version
```

2. Установите pip (если еще не установлен):
```bash
sudo apt update
sudo apt install python3-pip
```

3. Установите venv (если еще не установлен):
```bash
sudo apt install python3-venv
```

## Установка и настройка бота

1. Клонируйте репозиторий (если используете Git) или распакуйте архив с ботом:
```bash
git clone <URL_репозитория>
# или распакуйте архив
cd simplebot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` в корневой директории проекта:
```bash
touch .env
nano .env
```

5. Добавьте в файл `.env` следующие строки:
```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
DEEPSEEK_API_KEY=ваш_ключ_api
```

### Получение необходимых токенов

1. Для получения TELEGRAM_BOT_TOKEN:
   - Откройте Telegram и найдите @BotFather
   - Отправьте команду `/newbot`
   - Следуйте инструкциям для создания нового бота
   - Скопируйте полученный токен

2. Для получения DEEPSEEK_API_KEY:
   - Зарегистрируйтесь на сайте DeepSeek
   - Перейдите в раздел API
   - Создайте новый ключ API
   - Скопируйте полученный ключ

## Запуск бота как системный сервис

Для автоматического запуска бота при старте системы, мы настроим systemd сервис:

1. Создайте файл сервиса:
```bash
sudo nano /etc/systemd/system/telegrambot.service
```

2. Добавьте следующее содержимое (замените пути на актуальные для вашей системы):
```ini
[Unit]
Description=Telegram Bot Service
After=network.target

[Service]
Type=simple
User=ваш_пользователь
WorkingDirectory=/home/ваш_пользователь/projects/simplebot
Environment="PATH=/home/ваш_пользователь/projects/simplebot/venv/bin"
ExecStart=/home/ваш_пользователь/projects/simplebot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Перезагрузите демон systemd:
```bash
sudo systemctl daemon-reload
```

4. Включите автозапуск сервиса:
```bash
sudo systemctl enable telegrambot
```

5. Запустите сервис:
```bash
sudo systemctl start telegrambot
```

### Полезные команды для управления сервисом

- Проверка статуса:
```bash
sudo systemctl status telegrambot
```

- Остановка сервиса:
```bash
sudo systemctl stop telegrambot
```

- Перезапуск сервиса:
```bash
sudo systemctl restart telegrambot
```

- Просмотр логов сервиса:
```bash
sudo journalctl -u telegrambot -f
```

## Запуск бота

1. Убедитесь, что вы находитесь в директории проекта и виртуальное окружение активировано:
```bash
# Активация виртуального окружения (если еще не активировано)
source venv/bin/activate
```

2. Запустите бота:
```bash
python bot.py
```

## Проверка работы бота

1. Откройте Telegram
2. Найдите своего бота по имени, которое вы указали при создании
3. Отправьте команду `/start`
4. Бот должен ответить приветственным сообщением

## Решение проблем

Если бот не запускается, проверьте:

1. Правильность токенов в файле `.env`
2. Активировано ли виртуальное окружение (в терминале должен быть префикс `(venv)`)
3. Все ли зависимости установлены корректно
4. Логи в терминале на наличие ошибок

## Остановка бота

Для остановки бота нажмите `Ctrl+C` в терминале, где запущен бот.

## Дополнительные команды

- Деактивация виртуального окружения:
```bash
deactivate
```

- Просмотр логов в реальном времени:
```bash
tail -f bot.log
```

(｡♥‿♥｡) Удачной работы с ботом! При возникновении вопросов обращайтесь к разработчикам! 