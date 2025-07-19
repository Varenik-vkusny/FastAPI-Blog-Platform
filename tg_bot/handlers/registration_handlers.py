import httpx
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..core.config import settings


API_BASE_URL = settings.api_base_url


class RegisterStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()


router = Router()


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