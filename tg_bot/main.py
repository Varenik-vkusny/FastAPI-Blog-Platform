import logging
import asyncio
from aiogram import Router, Dispatcher, Bot
from .core.config import settings
from .handlers import common, auth_handlers, post_handlers, registration_handlers


router = Router()


async def main():
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(registration_handlers.router)
    dp.include_router(auth_handlers.router)
    dp.include_router(post_handlers.router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())