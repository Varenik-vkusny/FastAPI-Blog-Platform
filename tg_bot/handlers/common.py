from aiogram import Router, types
from aiogram.filters import CommandStart
from ..keyboards.reply_kb import main_kb

router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer('Привет! Я телеграм бот, у которого бэкенд написан на FastAPI фреймворке.', reply_markup=main_kb)


@router.message()
async def echo_handler(message: types.Message):
    await message.answer('Неизвестное сообщение.')
