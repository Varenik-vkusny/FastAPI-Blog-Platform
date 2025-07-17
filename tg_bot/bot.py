import os
import httpx
import logging
import asyncio
from aiogram import Router, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from pathlib import Path
from dotenv import load_dotenv

current_file_path = Path(__file__)

project_root = current_file_path.parent.parent

env_path = project_root / ".env"

load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_BASE_URL = os.getenv('API_BASE_URL')


class RegisterStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Регистрация'),
            KeyboardButton(text='Вход')
        ],
        [
            KeyboardButton(text='Посты'),
            KeyboardButton(text='Создать пост')
        ]
    ]
)


router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer('Привет! Я телеграм бот, у которого бэкенд написан на FastAPI фреймворке.', reply_markup=main_kb)


@router.message(F.text == 'Регистрация')
async def start_register(message: types.Message, state: FSMContext):

    await message.answer('Давайте начнем регистрацию! Введите ник: ')

    await state.set_state(RegisterStates.waiting_for_username)


@router.message(RegisterStates.waiting_for_username)
async def register_username_handler(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer('Вы не ввели ник! Попробуйте еще раз.')
        return
    
    await state.update_data(username=message.text)

    await message.answer('Отлично! Теперь введите пароль:')

    await state.set_state(RegisterStates.waiting_for_password)


@router.message(RegisterStates.waiting_for_password)
async def register_password_handler(message: types.Message, state: FSMContext):

    user_data = await state.get_data()
    username = user_data.get['username']
    password = message.text

    register_data = {
        'username': username,
        'password': password
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f'{API_BASE_URL}/register', json=register_data)

            if response.status_code != 201:
                error_detail = response.json().get('detail', 'Неизвестная ошибка')
                await message.answer(f'Произошла ошибка: {error_detail}')
            else:
                new_user = response.json()
                await message.answer(f'Регистрация прошла успешно! Ваш id: {new_user['id']}, ваш ник: {new_user['username']}')
        except httpx.RequestError:
            await message.answer('не удалось подключиться к серверу')
    await state.clear()