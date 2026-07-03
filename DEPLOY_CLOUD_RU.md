# Деплой на Cloud.ru VM

Бот работает через long polling, поэтому домен, webhook и открытые HTTP-порты не нужны. На сервере должен быть интернет наружу и SSH-доступ для управления.

## 1. Подготовить сервер

Ubuntu 24.04, 1 vCPU, 1 GB RAM, 10 GB SSD достаточно.

```bash
sudo apt update
sudo apt install -y git python3 python3-venv
```

## 2. Скачать код

```bash
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/shesocold_bot.git
cd shesocold_bot
```

## 3. Установить зависимости

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 4. Создать `.env`

```bash
nano .env
```

Вставить:

```env
BOT_TOKEN=токен_от_BotFather
```

## 5. Запустить как службу

```bash
sudo cp deploy/shesocold-bot.service /etc/systemd/system/shesocold-bot.service
sudo systemctl daemon-reload
sudo systemctl enable shesocold-bot
sudo systemctl start shesocold-bot
```

Проверка:

```bash
sudo systemctl status shesocold-bot
sudo journalctl -u shesocold-bot -f
```

## 6. Обновлять код

```bash
cd /home/ubuntu/shesocold_bot
git pull
.venv/bin/pip install -r requirements.txt
sudo systemctl restart shesocold-bot
```

Важно: локального бота на ноутбуке нужно остановить, иначе Telegram выдаст конфликт двух запущенных экземпляров.

## Если Cloud.ru не достаёт до Telegram

Проверка:

```bash
curl -I https://google.com
curl -4 -v --connect-timeout 10 https://api.telegram.org
```

Если Google открывается, а `api.telegram.org:443` уходит в timeout, бот будет падать с `TelegramNetworkError: Request timeout error`. Это проблема сетевого доступа ВМ к Telegram API.

Что можно сделать без ожидания поддержки: пустить Telegram-запросы через прокси.

Логин и пароль в прокси-строке, если они есть, выдаёт именно прокси-сервис. Это не логин Cloud.ru, не GitHub и не пользователь сервера.

Поддерживаются такие варианты:

```env
TELEGRAM_PROXY=http://host:port
TELEGRAM_PROXY=http://user:password@host:port
TELEGRAM_PROXY=socks5://user:password@host:port
```

После изменения `.env` обновить зависимости и проверить доступ:

```bash
.venv/bin/pip install -r requirements.txt
.venv/bin/python check_telegram.py
```

Если проверка пишет `Telegram API check: OK`, перезапустить службу:

```bash
sudo systemctl restart shesocold-bot
sudo systemctl status shesocold-bot
```

Если без прокси `check_telegram.py` падает с timeout, а с прокси тоже падает, значит конкретный прокси не подходит или Cloud.ru режет этот маршрут. Тогда нужны другой прокси/VPN или другой хостинг, где `curl -4 -I https://api.telegram.org` работает.
