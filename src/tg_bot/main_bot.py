import asyncio
import logging
from aiogram import Bot, Dispatcher
from src.backend.config import settings
from .handlers import auth_handlers, registration_handlers, post_handlers, common

logging.basicConfig(level=logging.INFO)

async def main():

    logging.info('Запускаю бота')

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(registration_handlers.router)
    dp.include_router(auth_handlers.router)
    dp.include_router(post_handlers.router)

    await dp.start_polling(bot)

    logging.info('Бот запущен')


if __name__ == '__main__':
    asyncio.run(main())