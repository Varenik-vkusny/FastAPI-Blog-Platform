from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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