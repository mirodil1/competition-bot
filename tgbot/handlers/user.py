from cgitb import text
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
            await message.answer(f"Сизни ушбу ботга <a href='tg://user?id={args}'>{user['full_name']}</a> таклиф қилди!")
            await message.answer(
                "'📲 Рақамни юбориш' тугмасини босган ҳолда рақамингизни юборинг!", 
                reply_markup=phone
            )
            try:
                text = "👤 Янги иштирокчи қўшилди\n"
                text += f"🎗 Сизнинг балингиз {user['score']}, кўпроқ дўстларингизни таклиф этиб баллингизни оширинг!"
                bot = message.bot
                await bot.send_message(chat_id=int(args), text=text)
            except Exception as e:
                print(e)
        else:
            await message.answer(
                "'📲 Рақамни юбориш' тугмасини босган ҳолда рақамингизни юборинг!", 
                reply_markup=phone
            )
    except:
        user = dict(await db.select_user(id=message.from_user.id))
        if user['phone_number'] is not None:
            await message.answer(
                text="Қуйидаги  менюдан керакли бўлимни танланг 👇",
                reply_markup=menu
            )
        else:
            await message.answer(
                "'📲 Рақамни юбориш' тугмасини босган ҳолда рақамингизни юборинг!", 
                reply_markup=phone
            )


async def verify_phone_number(message: Message):
    if message.contact.user_id == message.from_user.id:

        phone_number = message.contact.phone_number
        id = message.from_user.id

        await db.set_phone_number(phone_number=phone_number, id=id)

        intro = """<b>"IT Masters" ҳамда "Excel Hacks" ҳамкорлигида ташкил \
                этилган техно конкурсда иштирок этинг ва қуйидаги совринлардан \
                бирини ютиб олинг!</b>\n\n"""
        intro += "🥇 <b>1-ўрин</b>: RGB Gaming Combo 4 in 1 (Клавиатура, сичқонча, қулоқчинлар ва коврик)\n"
        intro += "🥈 2-ўрин: UzBrand ноутбук сумкаси ва клавиатура.\n"
        intro += "🥉 3-ўрин: Freemotion B525 Wireless қулоқчинлари."

        sign_up = "<b>Табриклаймиз ✅</b>,  Сиз рўйхатдан муваффақиятли ўтдингиз! Совринлар рўйхати юқоридаги постда 👆\n\n"
        sign_up += "<b>Қуйидаги «Танловда иштирок этиш» бўлимини танланг 👇 👇</b>"
        await message.answer(text=intro, reply_markup=menu)
        await message.answer(text=sign_up)
    else:
        await message.answer("Илтимос, '📲 Рақамни юбориш' тугмасини босган ҳолда рақамингизни юборинг!", reply_markup=phone)


async def join_comp(message: Message):
    text = "Балл тўплаш учун сизга бериладиган реферал (махсус) линк орқали одам таклиф қилишингиз керак бўлади."
    text+= "Таклиф этилган ҳар бир одам учун <b>5 балл</b> берилади"

    await message.answer(text=text, reply_markup=ref_link_button)


async def generate_depp_link(call: CallbackQuery):
    text = "<b>Энг сара 10 та совринлардан бирини ютиб олишни истайсизми?"
    text += "Унда «IT Masters» ҳамда «Excel Hacks» ҳамкорлигида ташкил этилган танловда қатнашиб, омадингизни синаб кўринг!\n\n"
    text += "Танловда иштирок этиш учун 👇</b>"
    link = await get_start_link(call.from_user.id)
    text += link

    msg =  await call.message.answer(text=text)
    await msg.reply("👆 Юқоридаги сизнинг реферал линк/ҳаволангиз. Уни кўпроқ танишларингизга улашинг. Омад!")


async def terms_and_policy(message: Message):
    text = "<b>ТАНЛОВ ШАРТЛАРИ:</b>\n\n"
    text += "❗️Ушбу танловда 10та ғолиблар тўплаган балларига қараб аниқланади.\n\n"
    text += "<b>Баллар қандай тўпланади?</b>\n\n"
    text += """БОТда келтирилган 2 та каналга обуна бўлгач, "Аъзо бўлдим" тугмасини босишингиз билан, сизга махсус реферал линк (ҳавола) берилади.\
Ўша линк орқали обуна бўлган ҳар бир инсон учун сизга 5 баллдан бериб борилади. \
Қанча кўп балл йиғсангиз, ғолиб бўлиш имкониятингиз шунча ортиб боради.\n\n"""
    text += "⌛️ <i>Танлов 31 октябрь куни 23:59да якунланади.\n\n</i>"
    text += "<b>❗️Диққат! Сунъий (ўлик аккаунтлар қўшган) накрутка ва х.к. лардан фойдаланганлар танловдан четлаштирилади!</b>"

    await message.answer(text=text)


async def get_all_users(message: Message):
    current_user = dict(await db.select_user(id=message.from_user.id))
    users_record = list(await db.select_all_users())
    users = [dict(user) for user in users_record][:20]

    text = "<b>📊 Ботимизга энг кўп дўстини таклиф қилиб балл тўплаганлар рўйҳати:</b>\n\n"
    place = 1
    for user in users:
        text += f"🏅 <b>{place}-ўрин: {user['full_name']} • {user['score']} балл</b>\n"
        place += 1

    text += f"\n✅ <b>Сизда {current_user['score']} балл</b>.  Кўпроқ дўстларингизни таклиф этиб баллингизни оширинг!"

    await message.answer(text=text)


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_message_handler(verify_phone_number, content_types=ContentType.CONTACT)
    dp.register_message_handler(join_comp, text="🎁 ТАНЛОВДА ИШТИРОК ЭТИШ")
    dp.register_callback_query_handler(generate_depp_link, text="join")
    dp.register_message_handler(terms_and_policy, text="📝 Шартлар")
    dp.register_message_handler(get_all_users, text="📊 Рейтинг")