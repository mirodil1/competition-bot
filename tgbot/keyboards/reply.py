from aiogram .types import ReplyKeyboardMarkup, KeyboardButton

phone = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="📲 Raqamni yuborish", request_contact=True)
        ]
    ],
    resize_keyboard=True
)

menu = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="➡️ TANLOVDA ISHTIROK ETISH")
        ],
        [
            KeyboardButton(text="🔢 Reyting"),
            KeyboardButton(text="ℹ️ Ma’lumot")
        ]
    ],
    resize_keyboard=True
)