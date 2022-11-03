from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import filters, FSMContext

from tgbot.misc.states import Message
from tgbot.keyboards.inline import  send_msg_button, response_callback_confirm
from tgbot.misc.db import db

import asyncio


async def admin_start(message: types.Message):
    await message.reply("Hello, admin!")

async def ads(message: types.Message):
        await message.answer("Istagan xabaringizni kiriting")
        await Message.message.set()

async def prepare_to_send(message: types.Message, state: FSMContext):
    counter = await db.count_users()
    bot = message.bot

    await bot.forward_message(from_chat_id=message.from_user.id, chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(f"Xabar {counter} ta foydalanuvchiga yuboriladi.", reply_markup=send_msg_button)
    async with state.proxy() as data:
        data['message'] = message.message_id
        data['from_user_id'] = message.from_user.id

async def confirmation(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    bot = call.message.bot
    call_data = callback_data['confirm']
    count = 0
    if call_data == 'agree':
        data = await state.get_data()
        from_user_id = data.get('from_user_id')
        message_id = data.get('message')
        users = await db.select_all_users()
        await call.message.edit_text("Xabar yuborilyapti")
        await state.finish()
        for user in users:
            user = dict(user)
            try:
                await bot.copy_message(from_chat_id=from_user_id, chat_id=user['telegram_id'], message_id=message_id)
                count+=1
            except:
                print(f"Bot was blocked by {user}")
            await asyncio.sleep(0.05)
        await call.message.answer(f"Xabar {count} ta foydalanuvchiga yuborildi.")
    elif call_data == 'disagree':
        await call.message.delete()
        await call.message.answer("Bekor qilindi.")
        await call.answer(cache_time=15)
        await state.finish()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)

    dp.register_message_handler(ads, commands=["reklama"], is_admin=True)
    dp.register_message_handler(prepare_to_send, content_types=[types.ContentType.ANY], state=Message.message, is_admin=True)
    dp.register_callback_query_handler(confirmation, response_callback_confirm.filter(), state=Message.message, is_admin=True)