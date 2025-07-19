import logging
import asyncio
from aiogram import Router, Dispatcher, Bot
from .core.config import settings
from .handlers import common, user_commands


router = Router()


async def main():
    bot = Bot(token=settings.bot_token, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(user_commands.router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())