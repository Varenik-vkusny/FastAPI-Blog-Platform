import httpx
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from ..keyboards.inline_kb import get_inline_kb
from ..core.config import settings
from .auth_handlers import users_token


API_BASE_URL = settings.api_base_url

class CreatePostStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()


class UpdatePostStates(StatesGroup):
    waiting_for_new_title = State()
    waiting_for_new_content = State()


router = Router()


# ---GET POSTS BLOCK---
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
                
                post_id = post['id'] 
                likes_count = post.get('likes_count', 0)       

                await message.answer(text=text, parse_mode='Markdown', reply_markup=get_inline_kb(post_id=post_id, current_likes=likes_count))
        except httpx.HTTPStatusError as e:
            await message.answer(f'Произошла ошибка при загрузка постов: {e.response.status_code}')
        except httpx.RequestError:
            await message.answer('Не удалось подключиться к серверу')


# ---LIKE HANDLER BLOCK---
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
                
                await callback.answer(text=response.json().get('detail'), show_alert=False)
        except httpx.RequestError:
            await callback.answer('Не удалось подключиться к серверу.', show_alert=True)


# ---EDIT POST HANDLER BLOCK---
@router.callback_query(F.data.startswith('update_'))
async def update_post_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    post_id = int(callback.data.split('_')[1])

    await state.update_data(post_id=post_id)

    await callback.message.answer('Введите новый заголовок:')
    await state.set_state(UpdatePostStates.waiting_for_new_title)


@router.message(UpdatePostStates.waiting_for_new_title)
async def update_title_handler(message: types.Message, state: FSMContext):

    await state.update_data(title=message.text)

    await message.answer('Отлично! Теперь введите новый текст для поста:')

    await state.set_state(UpdatePostStates.waiting_for_new_content)


@router.message(UpdatePostStates.waiting_for_new_content)
async def update_content_handler(message: types.Message, state: FSMContext):

    update_post_data = await state.get_data()
    post_id = update_post_data.get('post_id')
    title = update_post_data.get('title')
    content = message.text

    user_id = message.from_user.id
    access_token = users_token.get(user_id)

    if not access_token:
        await message.answer('Чтобы редактировать пост нужно авторизоваться!')
        return
    
    post_data = {
        'title': title,
        'content': content
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(f'{API_BASE_URL}/post/{post_id}', json=post_data, headers=headers)

            if response.status_code == 401:
                await message.answer('Ваша сессия истекла, пожалуйста авторизуйтесь снова!')
                state.clear()
                return
            if response.status_code != 200:
                error_detail = response.json().get('detail', 'Неизвестная ошибка!')
                await message.answer(f'Произошла ошибка: {error_detail}')
                state.clear()
                return

            post = response.json()

            await message.answer(f'Ваш пост успешно отредактирован!')

            state.clear()
        except httpx.RequestError:
            await message.answer('Не удалось подключиться к серверу.')
            state.clear()


# ---DELETE POST HANDLER BLOCK---
@router.callback_query(F.data.startswith('delete_'))
async def delete_post_handler(callback: types.CallbackQuery):
    
    user_id = callback.from_user.id

    access_token = users_token.get(user_id)

    if not access_token:
        await callback.message.answer('Чтобы удалить пост вы должны быть авторизованы!')
        return
    
    post_id = int(callback.data.split('_')[1])

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f'{API_BASE_URL}/post/{post_id}', headers=headers)

            if response.status_code == 401:
                await callback.message.answer('Ваша сессия истекла, пожалуйста авторизуйтесь снова!')
                return
            
            if response.status_code != 200:
                error_detail = response.json().get('detail', 'Неизвестная ошибка!')
                await callback.message.answer(f'Произошла ошибка: {error_detail}')
                return
            
            await callback.answer(f'Пост №{post_id} успешно удален!', show_alert=False)
        except httpx.RequestError:
            await callback.message.answer('Не удалось подключиться к серверу.')


# ---CREATE POST BLOCK---
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