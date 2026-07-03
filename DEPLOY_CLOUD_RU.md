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

Варианты:

1. Проверить правила сети Cloud.ru: исходящий TCP 443 должен быть разрешён.
2. Использовать HTTP-прокси и добавить его в `.env`:

```env
TELEGRAM_PROXY=http://user:password@host:port
```

После изменения `.env`:

```bash
sudo systemctl restart shesocold-bot
```

3. Если прокси не нужен, но Cloud.ru всё равно не открывает Telegram API, проще перенести бота на хостинг/сервер, где `curl -4 -I https://api.telegram.org` работает.
