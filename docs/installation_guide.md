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

## Автоматический деплой

Для автоматического обновления бота при каждом коммите, мы настроим GitHub Actions и деплой на сервер.

### 1. Настройка SSH-ключей

На вашем локальном компьютере:
```bash
# Генерируем SSH-ключ для деплоя
ssh-keygen -t ed25519 -C "deploy-key" -f ~/.ssh/deploy_key
```

На удалённом сервере:
```bash
# Добавьте публичный ключ в authorized_keys
echo "содержимое_deploy_key.pub" >> ~/.ssh/authorized_keys
```

### 2. Настройка GitHub Secrets

1. Перейдите в настройки вашего репозитория на GitHub
2. Выберите "Settings" -> "Secrets and variables" -> "Actions"
3. Добавьте следующие секреты:
   - `SSH_PRIVATE_KEY`: содержимое файла `~/.ssh/deploy_key`
   - `SERVER_HOST`: IP-адрес вашего сервера
   - `SERVER_USERNAME`: имя пользователя на сервере
   - `BOT_TOKEN`: токен вашего Telegram бота
   - `DEEPSEEK_API_KEY`: ваш ключ API DeepSeek

### 3. Создание GitHub Actions workflow

Создайте файл `.github/workflows/deploy.yml` в вашем репозитории:

```yaml
name: Deploy Bot

on:
  push:
    branches:
      - main  # или master, в зависимости от вашей основной ветки

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          echo -e "Host *\n\tStrictHostKeyChecking no\n\n" > ~/.ssh/config

      - name: Deploy to server
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${{ secrets.SERVER_USERNAME }}
        run: |
          # Копируем файлы на сервер
          rsync -avz -e "ssh -i ~/.ssh/deploy_key" \
            --exclude '.git*' \
            --exclude 'venv' \
            --exclude '__pycache__' \
            ./ ${{ secrets.SERVER_USERNAME }}@${{ secrets.SERVER_HOST }}:/home/${{ secrets.SERVER_USERNAME }}/projects/simplebot/

      - name: Update environment and restart bot
        env:
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
          SERVER_USERNAME: ${{ secrets.SERVER_USERNAME }}
          BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: |
          ssh -i ~/.ssh/deploy_key ${{ secrets.SERVER_USERNAME }}@${{ secrets.SERVER_HOST }} '
            cd ~/projects/simplebot
            echo "TELEGRAM_BOT_TOKEN=${{ secrets.BOT_TOKEN }}" > .env
            echo "DEEPSEEK_API_KEY=${{ secrets.DEEPSEEK_API_KEY }}" >> .env
            source venv/bin/activate
            pip install -r requirements.txt
            sudo systemctl restart telegrambot
          '
```

### 4. Настройка прав на сервере

На удалённом сервере добавьте право на перезапуск сервиса без пароля:
```bash
# Откройте sudoers файл
sudo visudo

# Добавьте строку (замените username на вашего пользователя):
username ALL=(ALL) NOPASSWD: /bin/systemctl restart telegrambot
```

### 5. Проверка деплоя

1. Закоммитьте и запушьте изменения в репозиторий:
```bash
git add .
git commit -m "Update bot code"
git push origin main
```

2. Проверьте статус деплоя:
   - Откройте GitHub -> Actions
   - Посмотрите статус последнего workflow
   - Проверьте статус бота на сервере:
     ```bash
     sudo systemctl status telegrambot
     ```

### Решение проблем при деплое

1. Проверьте права доступа:
```bash
# На сервере
ls -la ~/projects/simplebot
sudo systemctl status telegrambot
journalctl -u telegrambot -f
```

2. Проверьте логи GitHub Actions:
   - Откройте GitHub -> Actions -> Последний workflow
   - Изучите логи каждого шага

3. Проверьте SSH подключение:
```bash
# Локально
ssh -i ~/.ssh/deploy_key username@server_host
```

(｡♥‿♥｡) Удачной работы с ботом! При возникновении вопросов обращайтесь к разработчикам! 