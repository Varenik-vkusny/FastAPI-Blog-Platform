from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_inline_kb(post_id: int, current_likes: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f'👍 {current_likes}', callback_data=f'like_{post_id}'),
                InlineKeyboardButton(text='Редактировать пост', callback_data=f'update_{post_id}'),
                InlineKeyboardButton(text='Удалить пост', callback_data=f'delete_{post_id}')
            ]
        ]
    )

    return keyboard