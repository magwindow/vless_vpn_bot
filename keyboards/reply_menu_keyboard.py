from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="ℹ️ Статус"), KeyboardButton(text="⚡️ Подключиться!")],
        [KeyboardButton(text="🔥 Купить"), KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True)
