import asyncio
import os
from pathlib import Path

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent


async def main() -> None:
    load_dotenv(BASE_DIR / ".env")

    token = os.getenv("BOT_TOKEN")
    proxy = os.getenv("TELEGRAM_PROXY")

    if not token or token == "your_telegram_bot_token_here":
        raise SystemExit("BOT_TOKEN is missing in .env")

    session = AiohttpSession(proxy=proxy) if proxy else AiohttpSession()
    bot = Bot(token=token, session=session)

    try:
        me = await bot.get_me()
    except Exception as exc:
        print("Telegram API check: FAILED")
        print(f"{type(exc).__name__}: {exc}")
        raise SystemExit(1) from exc
    finally:
        await bot.session.close()

    proxy_state = "with proxy" if proxy else "without proxy"
    print(f"Telegram API check: OK {proxy_state}")
    print(f"Bot: @{me.username} ({me.full_name})")


if __name__ == "__main__":
    asyncio.run(main())
