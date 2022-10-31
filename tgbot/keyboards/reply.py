from aiogram .types import ReplyKeyboardMarkup, KeyboardButton

phone = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="📲 Рақамни юбориш", request_contact=True)
        ]
    ],
    resize_keyboard=True
)

menu = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="🎁 ТАНЛОВДА ИШТИРОК ЭТИШ")
        ],
        [
            KeyboardButton(text="📊 Рейтинг"),
            KeyboardButton(text="📝 Шартлар")
        ]
    ],
    resize_keyboard=True
)