import httpx
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..core.config import settings


API_BASE_URL = settings.api_base_url
users_token = {}


class LoginStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()


router = Router()


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
