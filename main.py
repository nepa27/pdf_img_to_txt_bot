import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import questions


load_dotenv('.env')
TOKEN = os.environ.get('TELEGRAM_TOKEN')


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(questions.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
