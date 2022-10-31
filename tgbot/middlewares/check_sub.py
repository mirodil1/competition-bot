from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.misc.db import db
from tgbot.misc.subscription import check
from tgbot.keyboards.inline import subscription_button
from tgbot.keyboards.reply import menu

import asyncpg

class CheckSubscriptionMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        final_status = True     
        channels_record = await db.select_all_channels()
        channels = list(dict(channel) for channel in channels_record)
        if update.callback_query:
            user_id = update.callback_query.from_user.id
            if update.callback_query.data == "check_subs":
                for channel in channels:
                    status = await check(user_id=user_id, channel=channel['username'])
                    final_status *= status
                if final_status:
                    await update.callback_query.message.edit_text(text="Қуйидаги  менюдан керакли бўлимни танланг 👇")
                    return
                else:
                    await update.callback_query.answer(text="Ботдан тўлиқ фойдаланиш учун каналларга обуна бўлинг.", show_alert=True)
                    
        elif update.message:
            user_id = update.message.from_user.id
            if update.message.text in ['/start', '/help'] or update.message.reply_to_message or update.message.contact or "start" in update.message.text:
                return

        for channel in channels:

            if channel['status']:
                status = await check(user_id=user_id, channel=channel['username'])
                final_status *= status
            if not final_status:
                try:
                    await update.message.answer(text="Ботдан тўлиқ фойдаланиш учун қуйидаги каналларга обуна бўлинг.", disable_web_page_preview=True, reply_markup=await subscription_button(user_id, channels))
                    raise CancelHandler()
                except:
                    # await update.callback_query.message.answer(text="Ботдан тўлиқ фойдаланиш учун қуйидаги каналларга обуна бўлинг.", disable_web_page_preview=True, reply_markup=await subscription_button(user_id, channels))
                    raise CancelHandler()