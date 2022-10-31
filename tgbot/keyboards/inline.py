from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.misc.subscription import check
from tgbot.config import load_config

config = load_config(".env")
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')



ref_link_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👤Одам таклиф қилиб балл тўплаш", callback_data="join")
        ]
    ]
)

async def subscription_button(user, channels):

    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        if channel['status']:
            status = await check(user_id=user, channel=channel['username'])
        try:
            channel = await bot.get_chat(channel['username'])
        except:
            pass
        if not status:
            markup.insert(
                InlineKeyboardButton(text="{title}".format(title=channel.title), url=channel['invite_link'])
            )
    markup.insert(
        InlineKeyboardButton(text="✅ Обуна бўлдим", callback_data="check_subs")
    )
    return markup