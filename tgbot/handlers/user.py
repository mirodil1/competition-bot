from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Message, ContentType, CallbackQuery
from aiogram.dispatcher.filters.builtin import IsSenderContact
from aiogram.utils.deep_linking import get_start_link

from tgbot.keyboards.reply import phone, menu
from tgbot.keyboards.inline import ref_link_button
from tgbot.misc.db import db

import asyncpg

async def user_start(message: Message):
    try:
        args = message.get_args()

        await db.add_user(
            id=message.from_user.id,
            full_name=message.from_user.full_name,
            phone_number=None,
            username=message.from_user.username,
            score=5,
            joined_date=datetime.now()
        )
        if args:
            await db.update_user_score(id=int(args))

            await db.add_invited_users(
                user_offered_id=int(args),
                user_invited_id=message.from_user.id,
                created_at=datetime.now()
            )
            
            user = dict(await db.select_user(id=int(args)))
            await message.answer(f"Sizni ushbu botga <a href='tg://user?id={args}'>{user['full_name']}</a> taklif qildi!")
            await message.answer(
                "📲 Ro‘yxatdan o‘tish uchun telefon raqamingizni yuboring!", 
                reply_markup=phone
            )
            try:
                text = "🆕 Yangi ishtirokchi qo‘shildi!\n"
                text += f"🆙 Sizning balingiz — {user['score']}, Ko‘proq do‘stlaringizni taklif qilib, ballaringizni oshiring!"
                bot = message.bot
                await bot.send_message(chat_id=int(args), text=text)
            except Exception as e:
                print(e)
        else:
            await message.answer(
                "📲 Ro‘yxatdan o‘tish uchun telefon raqamingizni yuboring!", 
                reply_markup=phone
            )
    except:
        user = dict(await db.select_user(id=message.from_user.id))
        if user['phone_number'] is not None:
            await message.answer(
                text="Quyidagi menyudan kerakli bo'limni tanlang 👇",
                reply_markup=menu
            )
        else:
            await message.answer(
                "📲 Ro‘yxatdan o‘tish uchun telefon raqamingizni yuboring!", 
                reply_markup=phone
            )


async def verify_phone_number(message: Message):
    if message.contact.user_id == message.from_user.id:

        phone_number = message.contact.phone_number
        id = message.from_user.id

        await db.set_phone_number(phone_number=phone_number, id=id)

        intro = """<b>Sovrinlar ro‘yxati:</b>\n\n"""
        intro += "1️⃣  <b>1-, 2- va 3-o‘rin</b>— noutbuk;\n"
        intro += "2️⃣  <b> 4- va 5-o‘rin</b>— planshet;\n"
        intro += "3️⃣  <b> 6-, 7-, 8-, 9- va 10-o‘rin</b>— 300 ming so‘mdan pul mukofoti;\n"
        intro += "4️⃣  <b> 10-dan 20-o‘ringacha</b> — 200 ming so‘mdan pul mukofoti;\n"
        intro += "5️⃣  <b> 20-dan 30-o‘ringacha</b>— 100 ming so‘mdan pul mukofoti.\n\n"
        intro += "<b>Quyidagi “Tanlovda ishtirok etish” bo‘limini tanlang:👇</b>"
        await message.answer(text=intro, reply_markup=menu)
    else:
        await message.answer("📲 Ro‘yxatdan o‘tish uchun telefon raqamingizni yuboring!", reply_markup=phone)


async def join_comp(message: Message):
     
    text = "Ball to‘plash uchun sizga quyidagi taqdim etilgan referal (maxsus) link orqali odam taklif qilishingiz kerak bo‘ladi."
    text+= "Taklif qilingan har bir odam uchun sizga <b>5 ball</b> beriladi"

    await message.answer(text=text, reply_markup=ref_link_button)


async def generate_depp_link(call: CallbackQuery):
    text = "<b>10 ta noutbuk, 10 ta planshet, 500 ming, 300 ming va 100 ming so‘mlik pul mukofotlaridan birini qo‘lga kiritishni istaysizmi?"
    text += "Unda mazkur tanlovda qatnashing va g‘olib bo‘ling. Yutish juda oson!\n\n"
    text += "Tanlovda ishtirok etish uchun:👇\n</b>"
    link = await get_start_link(call.from_user.id)
    text += link

    msg =  await call.message.answer(text=text)
    await msg.reply("👆Yuqoridagi sizning referal (maxsus) link/havolangiz. Uni ko‘proq tanishlaringizga ulashing. Omad!")


async def terms_and_policy(message: Message):
    text = "<b>ℹ️ Tanlov haqida ma’lumot:</b>\n\n"
    text += "Ushbu tanlovda 30 nafar g‘olib to‘plagan ballariga qarab aniqlanadi.\n\n"
    text += "<b>Ballar qanday to‘planadi?</b>\n\n"
    text += "Botda keltirilgan 5 ta kanalga obuna bo‘lgach, “A’zo bo‘ldim”"
    text += "tugmasini bosiladi va maxsus referal link (havola) beriladi. "
    text += "O‘sha link orqali obuna bo‘lgan har bir inson uchun sizga 5 balldan berib boriladi. "
    text += "Qancha ko‘p ball yig‘sangiz, g‘olib bo‘lish imkoniyatingiz shuncha ortib boradi.\n\n"
    text += "<b>Tanlov 31-dekabr kuni 23:59 da yakunlanadi.\n\n</b>"
    text += "<b>❗️ Diqqat!</b> sun’iy (o‘lik akkauntlar qo‘shgan) nakrutka va boshqalardan foydalangan ishtirokchilar tanlovdan chetlashtiriladi!"

    await message.answer(text=text)


async def get_all_users(message: Message):
    current_user = dict(await db.select_user(id=message.from_user.id))
    users_record = list(await db.select_all_users())
    users = [dict(user) for user in users_record][:30]

    text = "<b>🔢 Eng ko‘p do‘stlarini taklif qilib, ball to‘plaganlar ro‘yxati:</b>\n\n"
    place = 1
    for user in users:
        text += f"<b>{place}-o'rin: {user['full_name']} • {user['score']} ball</b>\n"
        place += 1 
    text += f"\n<b>☑️ Sizda {current_user['score']} ball</b>. Ko‘proq do‘stlaringizni taklif qilib, ballaringizni oshiring!"



    await message.answer(text=text)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(verify_phone_number, content_types=ContentType.CONTACT)
    dp.register_message_handler(join_comp, text="➡️ TANLOVDA ISHTIROK ETISH")
    dp.register_callback_query_handler(generate_depp_link, text="join")
    dp.register_message_handler(terms_and_policy, text="ℹ️ Ma’lumot")
    dp.register_message_handler(get_all_users, text="🔢 Reyting")