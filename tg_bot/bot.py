import os
import httpx
import logging
import asyncio
from aiogram import Router, Dispatcher, types, Bot, F
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
users_token = {}


class RegisterStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()


class LoginStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()


class CreatePostStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Регистрация'),
            KeyboardButton(text='Войти')
        ],
        [
            KeyboardButton(text='Посты'),
            KeyboardButton(text='Создать пост')
        ]
    ]
)


def get_inline_kb(post_id: int, current_likes: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f'👍 {current_likes}', callback_data=f'like_{post_id}')
            ]
        ]
    )

    return keyboard


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

    await message.answer('Отлично! Теперь введите пароль (минимум 3 символа):')

    await state.set_state(RegisterStates.waiting_for_password)


@router.message(RegisterStates.waiting_for_password)
async def register_password_handler(message: types.Message, state: FSMContext):

    if len(message.text) < 3:
        await message.answer('Ваш пароль слишком маленький! Попробуйте еще раз.')
        return

    user_data = await state.get_data()
    username = user_data.get('username')
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


@router.message(F.text == 'Войти')
async def start_login(message: types.Message, state: FSMContext):
    await message.answer('Давайте начнем процесс аутентификации! Введите ваш ник: ')

    await state.set_state(LoginStates.waiting_for_username)


@router.message(LoginStates.waiting_for_username)
async def login_username_handler(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)

    await message.answer('Отлично! Теперь введите ваш пароль:')

    await state.set_state(LoginStates.waiting_for_password)


@router.message(LoginStates.waiting_for_password)
async def login_password_handler(message: types.Message, state: FSMContext):
    
    user_data = await state.get_data()
    username = user_data.get('username')
    password = message.text

    login_data = {
        'username': username,
        'password': password
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f'{API_BASE_URL}/token', data=login_data)

            if response.status_code != 200:
                error_detail = response.json().get('detail', 'Неправильный ник или пароль')
                await message.answer(f'Произошла ошибка: {error_detail}')
                return
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            user_id = message.from_user.id
            users_token[user_id] = access_token

            await message.answer('Вы успешно авторизованы!')
        except httpx.RequestError:
            await message.answer('Не удалось подключиться к серверу.')
    await state.clear()


@router.message(F.text == 'Посты')
async def get_posts_handler(message: types.Message, state: FSMContext):

    await message.answer('Загружаю посты')

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f'{API_BASE_URL}/posts')

            response.raise_for_status()

            posts = response.json()

            if not posts:
                await message.answer('Пока нет ни одно поста.')
                return
            
            for post in posts:

                text = (
                    f'📄 *{post['title']}*\n\n'
                    f'{post['content']}\n\n'
                    f'Автор: {post['owner']['username']} | {post['created_at']}'
                )

                likes_count = post.get('likes_count', 0)
                post_id = post['id']        

                await message.answer(text=text, parse_mode='Markdown', reply_markup=get_inline_kb(post_id=post_id, current_likes=likes_count))
        except httpx.HTTPStatusError as e:
            await message.answer(f'Произошла ошибка при загрузка постов: {e.response.status_code}')
        except httpx.RequestError:
            await message.answer('Не удалось подключиться к серверу')


@router.callback_query(F.data.startswith('like_'))
async def like_handler(callback: types.CallbackQuery):

    access_token = users_token.get(callback.from_user.id)

    if not access_token:
        await callback.answer('Вы должны быть авторизованы для того чтобы поставить лайк!', show_alert=True)
        return
    
    post_id = int(callback.data.split('_')[1])

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f'{API_BASE_URL}/post/{post_id}/like', headers=headers)

            if response.status_code == 401:
                await callback.answer('Ваша сессия истекла, пожалуйста войдите снова!', show_alert=True)
                return

            if response.status_code != 200:
                error_detail = response.json().get('detail', 'Ошибка при лайке поста')
                await callback.answer(f'Произошла ошибка: {error_detail}', show_alert=True)
                return
            
            get_response = await client.get(f'{API_BASE_URL}/posts')
            get_response.raise_for_status
            posts = get_response.json()

            post_to_update = next((p for p in posts if p['id'] == post_id))

            if post_to_update:

                new_kb = get_inline_kb(post_id=post_id, current_likes=post_to_update.get('likes_count', 0))

                await callback.message.edit_reply_markup(reply_markup=new_kb)
                
                await callback.answer(text=response.json().get('detail'))
        except httpx.RequestError:
            await callback.answer('Не удалось подключиться к серверу.', show_alert=True)
    await callback.answer(f'Вы лайкнули пост №{post_id}', show_alert=True)    


@router.message(F.text == 'Создать пост')
async def create_post_handler(message: types.Message, state: FSMContext):
    await message.answer('Давайте создадим новый пост! Введите титл для поста:')

    await state.set_state(CreatePostStates.waiting_for_title)


@router.message(CreatePostStates.waiting_for_title)
async def title_handler(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)

    await message.answer('Отлично! Теперь введите текст для поста:')

    await state.set_state(CreatePostStates.waiting_for_content)


@router.message(CreatePostStates.waiting_for_content)
async def content_handler(message: types.Message, state: FSMContext):

    user_id = message.from_user.id
    access_token = users_token.get(user_id)

    if not access_token:
        await message.answer('Вы не авторизованы!')
        await state.clear()
        return

    post_data = await state.get_data()
    title = post_data.get('title')
    content = message.text

    post_data = {
        'title': title,
        'content': content
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f'{API_BASE_URL}/posts', json=post_data, headers=headers)

            if response.status_code == 401:
                await message.answer('Ваша сессия истекла, пожалуйста войдите снова!')
                return
            elif response.status_code != 201:
                error_detail = response.json().get('detail', 'Неизвестная ошибка!')
                await message.answer(f'Произошла ошибка: {error_detail}')
            else:
                new_post = response.json()
                await message.answer(f'Ваш пост {new_post['title']} успешно создан!')
        except httpx.RequestError:
            await message.answer('Не удалось подключиться к серверу.')
    await state.clear()


@router.message()
async def echo_handler(message: types.Message):
    await message.answer('Неизвестное сообщение.')


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())