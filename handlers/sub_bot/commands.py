import asyncio
import datetime
import os
import subprocess
import types

from aiogram import Router, Bot, flags, Dispatcher, F
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand, \
    BotCommandScopeDefault
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender, ChatActionMiddleware
from aiogram.utils.media_group import MediaGroupBuilder

import FSM
import config
import markup.client_markup as client_markup
from elevenlab import conver_to_audio
from markup import admin_markup
from openai_ import AIGirlfriend
from db_ import db
from middlewares import ChatActionMiddleware
import replicas.replicas_sub_bot as replicas

commands_router = Router()
commands_router.message.middleware.register(ChatActionMiddleware())


async def check_media_and_notifications(bot: Bot):
    while True:
        bot_id = (await bot.get_me()).id
        listdir = os.listdir("media")
        for file in listdir:
            if file.split("_")[0] == str(bot_id):
                try:
                    msg = await bot.send_photo(config.ADMINS[0], photo=FSInputFile(f"media/{file}"))
                    file_id = msg.photo[-1].file_id
                    db.update_start_photo(bot_id, file_id)
                    os.remove(f"media/{file}")
                except Exception as ex:
                    print(ex)
        mailing = db.get_mailing(bot_id)
        if len(mailing) > 0:
            if mailing[0][5] == 0:
                mailing_id = mailing[0][0]
                text = mailing[0][2]
                photo = mailing[0][3]
                video = mailing[0][10]
                document = mailing[0][11]
                type_ = mailing[0][4]
                if type_ == "all":
                    users = db.get_all_users_by_bot_id(bot_id)
                else:
                    users = db.get_users_without_subscribe_by_bot_id(bot_id)
                # photos_result = []
                photo_file_id = None
                video_file_id = None
                document_file_id = None
                if photo is not None:
                    # for photo in photos.split(";"):
                    msg = await bot.send_photo(config.ADMINS[0], photo=FSInputFile(photo))
                    photo_file_id = msg.photo[-1].file_id
                    await msg.delete()
                    # photos_result.append(file_id)
                    os.remove(photo)
                elif video is not None:
                    msg = await bot.send_video(config.ADMINS[0], video=FSInputFile(video))
                    video_file_id = msg.video.file_id
                    await msg.delete()
                    os.remove(video)
                elif document is not None:
                    msg = await bot.send_document(config.ADMINS[0], document=FSInputFile(document))
                    document_file_id = msg.document.file_id
                    await msg.delete()
                    os.remove(document)

                counter = 0
                for user in users:
                    try:
                        db.update_mailing_count(mailing_id, counter, len(users))
                        # if counter % 100 == 0:
                        #     db.update_mailing_count(mailing_id, counter, len(users))
                        counter += 1
                        if photo_file_id is not None:
                            await bot.send_photo(chat_id=user[0], photo=photo_file_id, caption=text)
                        elif video_file_id is not None:
                            await bot.send_video(chat_id=user[0], video=video_file_id, caption=text)
                        elif document_file_id is not None:
                            await bot.send_document(chat_id=user[0], document=document_file_id, caption=text)
                        else:
                            await bot.send_message(user[0], text)

                        # if len(photos_result) > 0:
                        #     if len(photos_result) == 1:
                        #         await bot.send_photo(chat_id=user[0], photo=photos_result[0], caption=text)
                        #     else:
                        #         media_group = MediaGroupBuilder(caption=text)
                        #         for photo in photos_result:
                        #             media_group.add_photo(media=photo)
                        #         await bot.send_media_group(user[0], media_group.build())

                    except Exception as ex:
                        print(ex)
                db.update_mailing_done(mailing_id, counter)

        users = db.get_users_for_mailing(bot_id)
        for user in users:
            last_message_time = datetime.datetime.strptime(user[1], "%Y-%m-%d %H:%M:%S")
            if last_message_time + datetime.timedelta(hours=1) < datetime.datetime.now() and user[2] == 0:
                try:
                    db.update_mailing(bot_id, user[0], "is_send_1_hour")
                    await bot.send_message(user[0], config.message_mailing_1_hour)
                except Exception as ex:
                    print(ex)
            elif last_message_time + datetime.timedelta(days=1) < datetime.datetime.now() and user[3] == 0:
                try:
                    db.update_mailing(bot_id, user[0], "is_send_1_day")
                    await bot.send_message(user[0], config.message_mailing_1_day)
                except Exception as ex:
                    print(ex)
            elif last_message_time + datetime.timedelta(days=2) < datetime.datetime.now() and user[4] == 0:
                try:
                    db.update_mailing(bot_id, user[0], "is_send_2_day")
                    await bot.send_message(user[0], config.message_mailing_2_day)
                except Exception as ex:
                    print(ex)
            elif last_message_time + datetime.timedelta(days=3) < datetime.datetime.now() and user[5] == 0:
                try:
                    db.update_mailing(bot_id, user[0], "is_send_3_day")
                    await bot.send_message(user[0], config.message_mailing_3_day)
                except Exception as ex:
                    print(ex)
            elif last_message_time + datetime.timedelta(days=7) < datetime.datetime.now() and user[6] == 0:
                try:
                    db.update_mailing(bot_id, user[0], "is_send_7_day")
                    await bot.send_message(user[0], config.message_mailing_7_day)
                except Exception as ex:
                    print(ex)

        feedback_messages = db.get_feedback_messages_not_answer(bot_id)
        for message in feedback_messages:
            await bot.send_message(chat_id=message[1], text="На ваш вопрос пришел ответ из администрации: ", reply_to_message_id=message[10])
            if message[11] is not None:
                await bot.send_photo(message[1], photo=FSInputFile(message[11]), caption=message[9])
                os.remove(message[11])
            elif message[12] is not None:
                await bot.send_document(message[1], document=FSInputFile(message[12]), caption=message[9])
                os.remove(message[12])
            elif message[13] is not None:
                await bot.send_video(message[1], video=FSInputFile(message[13]), caption=message[9])
                os.remove(message[13])
            else:
                await bot.send_message(chat_id=message[1], text=message[9], reply_to_message_id=message[10])
            db.update_status_feedback_message("is_answer", 1)

        subscribes = db.get_subscribe_not_updated_after_payment(bot_id)
        for subscribe in subscribes:
            print(subscribe)
            _, count_minutes = db.get_count_minutes_by_rate(subscribe[12])[0]
            db.add_minutes(subscribe[1], bot_id, count_minutes)
            db.update_subscribe(subscribe[0])
            await bot.send_message(chat_id=subscribe[1], text="Платеж был подтвержден")
        await asyncio.sleep(10)


async def set_commands(bot):
    commands = [
        BotCommand(
            command="start",
            description="Главное меню",
        ),
        BotCommand(
            command="vip",
            description="Тарифы",
        ),
        BotCommand(
            command="subscription",
            description="Подписки",
        ),
    ]

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


async def on_bot_startup(dispatcher: Dispatcher, bot: Bot):
    await set_commands(bot)
    asyncio.create_task(check_media_and_notifications(bot))


@commands_router.message(CommandStart())
async def start(message: Message, bot: Bot):

    bot_ = await bot.get_me()
    bot_id = bot_.id

    utm_id = None
    promo = None
    promo_id = None
    if len(message.text.split(" ")) == 2:
        start_id = message.text.split(" ")[1]
        utm_in_db = db.get_mark_by_link(bot_id, f"https://t.me/{bot_.username}?start={start_id}")
        if len(utm_in_db) > 0:
            utm_id = utm_in_db[0][0]

        promo = db.get_promo_by_link(f"https://t.me/{bot_.username}?start={start_id}")
        if len(promo) > 0:
            promo_id = promo[0][0]

    if not db.exist_user(bot_id, message.from_user.id):
        db.add_user(bot_id, message.from_user.id, message.from_user.username, message.from_user.full_name, utm_id, promo_id)
    else:
        db.update_last_message_time(bot_id, message.from_user.id)
        if utm_id is not None:
            db.update_utm_id(bot_id, message.from_user.id, utm_id)
        if promo_id is not None:
            db.update_promo_id(bot_id, message.from_user.id, promo_id)

    prompt = db.get_prompt(bot_id)[0][0]
    if not len(db.get_history_by_user_id(bot_id, message.from_user.id)):
        db.add_row(bot_id, message.from_user.id, "system", prompt)
    start_message = db.get_start_message(bot_id)[0]
    if start_message[0] is not None:

        if start_message[1] is not None:
            await message.answer_photo(photo=start_message[1], caption=start_message[0], reply_markup=client_markup.create_start_markup())
        else:
            await message.answer(start_message[0], reply_markup=client_markup.create_start_markup())

    if promo_id is not None:
        rates = db.get_all_rates_by_bot_id(bot_id)
        await message.answer(f"Промокод <b>{promo[0][2]}</b> на скидку <b>{promo[0][3]}%</b> активирован", reply_markup=client_markup.create_markup_choice_rate(rates, bot_id))


@commands_router.message(Command('vip'))
async def vip(message: Message, bot: Bot):
    bot_id = (await bot.get_me()).id
    rates = db.get_all_rates_by_bot_id(bot_id)
    price_per_minute = db.get_price_per_minute(bot_id)[0][0]
    await message.answer(f"Минута моего аудио-ответа стоит {price_per_minute}₽. "
                         f"Твои сообщения на 100% бесплатные.\n\nКакой тариф выберешь?😉",
                         reply_markup=client_markup.create_markup_choice_rate(rates, bot_id))


@commands_router.message(Command('subscription'))
async def subscription(message: Message, bot: Bot):
    bot_id = (await bot.get_me()).id
    total_length = db.get_total_lenght_by_user(message.from_user.id, bot_id)[0][0]
    total_length = 0 if total_length is None else total_length
    user_minutes = db.get_minutes_by_user(bot_id, message.from_user.id)
    if total_length < float(user_minutes) * 60:
        await message.answer(f"У вас есть {round((float(user_minutes) * 60 - total_length) / 60)} доступных минут")
    else:
        await message.answer(f"У вас нет активных подписок. Перейти к покупке?",
                             reply_markup=client_markup.create_markup_subscribe(bot_id))


@commands_router.message(FSM.FSMUser.get_text_feedback)
async def get_text_feedback(message: Message, state: FSMContext, bot: Bot):
    bot_id = (await bot.get_me()).id
    message_text = message.text
    user = db.get_user_by_user_id(message.from_user.id, bot_id)[0]
    if not user[15]:
        photo, video, document = None, None, None
        if message.photo is not None:
            message_text = message.caption
            file = await bot.get_file(message.photo[-1].file_id)
            file_path = file.file_path
            photo = f"feedback/{bot_id}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, photo)
        elif message.video is not None:
            message_text = message.caption
            file = await bot.get_file(message.video.file_id)
            file_path = file.file_path
            video = f"feedback/{bot_id}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, video)
        elif message.document is not None:
            message_text = message.caption
            file = await bot.get_file(message.video.file_id)
            file_path = file.file_path
            document = f"feedback/{bot_id}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, document)
        else:
            if message.text is None:
                await message.answer("Вопрос должен содержать текст или медиа вложение",
                                     reply_markup=client_markup.create_start_markup())
                return
        db.add_feedback_message(message.from_user.id, bot_id, message_text, message.message_id, photo=photo, video=video, document=document)
    await message.answer("Вопрос отправлен, ожидайте ответа", reply_markup=client_markup.create_start_markup())
    await state.clear()


# @commands_router.message(FSM.FSMUser.get_promo)
# async def get_promo(message: Message, state: FSMContext, bot: Bot):
#     promo_title = message.text
#     data = await state.get_data()
#     rate_id = data["rate_id"]
#     bot_id = data["bot_id"]
#     await bot.delete_message(message.from_user.id, data["msg_id"])
#     await message.delete()
#     promo_id, discount = db.check_promo(bot_id, promo_title, message.from_user.id)
#     if not promo_id:
#         await message.answer("Данного промокода не существует, либо у него закончились активации, попробуйте другой промокод", reply_markup=client_markup.create_markup_cancel())
#         return
#
#     pay_types = db.get_pay_types(bot_id)
#     await message.answer(f'Выберите способ оплаты', parse_mode="HTML", disable_web_page_preview=True,
#                                   reply_markup=client_markup.create_markup_pay_types(pay_types, rate_id, promo_id))
#     await state.clear()


@commands_router.message(FSM.FSMUser.get_photo_document_pay)
async def get_photo_document_pay(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.photo is not None or message.document is not None:
        count_minutes, amount, amount_dollar = db.get_amount_by_rate_id(data["rate_id"])
        pay_type = db.get_pay_type_by_id(data["pay_type_id"])
        if data["promo_id"] != "None":
            promo = db.get_promo(int(data["promo_id"]))
            discount_percent = int(promo[0][3])
            amount_with_discount = round(amount * (1 - discount_percent / 100), 2)
            amount_with_discount_dollar = round(amount_dollar * (1 - discount_percent / 100), 2)
        else:
            amount_with_discount = amount
            amount_with_discount_dollar = amount_dollar
        bot_id, _ = db.get_count_minutes_by_rate(data["rate_id"])[0]
        mark_id = db.get_mark_id_by_user_id(bot_id, message.from_user.id)
        row_id = db.add_payment(None, message.from_user.id, bot_id, amount_with_discount, mark_id, data["promo_id"], pay_type[2], data["rate_id"])
        caption = f'<b>💰 Подтвердите покупку.</b>\n\nПользователь:'\
                  f' <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>' \
                  f' (id: {message.from_user.id})\nТариф: <b>{count_minutes} минут - {amount} руб</b>\n' \
                  f'Сумма к оплате: <b>{amount_with_discount}₽ / {amount_with_discount_dollar}$</b>.\n' \
                  f'Платежная система: <b>{pay_type[2]}</b>' \

        for admin in config.ADMINS:

            try:
                if message.photo is not None:
                    await bot.send_photo(admin, message.photo[-1].file_id, caption=caption,
                                         reply_markup=client_markup.create_markup_accept_pay(message.from_user.id, row_id, data["rate_id"]))
                elif message.document is not None:
                    await bot.send_document(admin, message.document.file_id, caption=caption,
                                         reply_markup=client_markup.create_markup_accept_pay(message.from_user.id, row_id, data["rate_id"]))
            except:
                pass
        await message.answer("Ожидайте подтверждения оплаты администратором...")
        await state.clear()


@commands_router.message(F.text == replicas.rates)
async def rates(message: Message, bot: Bot):
    bot_id = (await bot.get_me()).id
    rates = db.get_all_rates_by_bot_id(bot_id)
    price_per_minute = db.get_price_per_minute(bot_id)[0][0]
    await message.answer(f"Минута моего аудио-ответа стоит {price_per_minute}₽. "
                                         f"Твои сообщения на 100% бесплатные.\n\nКакой тариф выберешь?😉",
                                         reply_markup=client_markup.create_markup_choice_rate(rates, bot_id))



@commands_router.message(F.text == replicas.subscribe)
async def subscribe(message: Message, bot: Bot):
    bot_id = (await bot.get_me()).id
    total_length = db.get_total_lenght_by_user(message.from_user.id, bot_id)[0][0]
    total_length = 0 if total_length is None else total_length
    user_minutes = db.get_minutes_by_user(bot_id, message.from_user.id)
    if total_length < float(user_minutes) * 60:
        await message.answer(f"У вас есть {round((float(user_minutes) * 60 - total_length) / 60)} доступных минут")
    else:
        await message.answer(f"У вас нет активных подписок. Перейти к покупке?",
                             reply_markup=client_markup.create_markup_subscribe(bot_id))


@commands_router.message(F.text == replicas.feedback)
async def feedback(message: Message, bot: Bot, state: FSMContext):
    await message.answer(
        "Ваш вопрос будет отправлен в Тех. поддержку. Срок ответа 3 рабочих дня.\n\nЗадайте ваш вопрос текстом, фотографией или любым другим медиавложением:",
        reply_markup=client_markup.create_markup_cancel())
    await state.set_state(FSM.FSMUser.get_text_feedback)


@commands_router.message(flags={"long_operation": "record_voice"})
async def all_messages(message: Message, bot: Bot, state: FSMContext):

    message_text = message.text
    bot_ = (await bot.get_me())
    bot_id = bot_.id

    # promo = db.get_promo_by_link(f"https://t.me/{bot_.username}?start={message.text}")
    promo = db.get_promo_by_name(message_text, bot_id)
    if len(promo) > 0:
        db.update_promo_id(bot_id, message.from_user.id, promo[0][0])
        rates = db.get_all_rates_by_bot_id(bot_id)
        await message.answer(f"Промокод <b>{promo[0][2]}</b> на скидку <b>{promo[0][3]}%</b> активирован", reply_markup=client_markup.create_markup_choice_rate(rates, bot_id))
    else:

        db.update_last_message_time(bot_id, message.from_user.id)
        voice_id = db.get_voice_id(bot_id)[0][0]
        total_length = db.get_total_lenght_by_user(message.from_user.id, bot_id)[0][0]
        total_length = 0 if total_length is None else total_length
        user_minutes = db.get_minutes_by_user(bot_id, message.from_user.id)

        if total_length < float(user_minutes) * 60:

            prompt = db.get_prompt(bot_id)[0][0]
            history = db.get_history_by_user_id(bot_id, message.from_user.id)
            length_messages = len(prompt)
            last_index = 0
            for index in range(len(history) - 1, -1, -1):

                if length_messages + len(history[index]) > config.max_tokens:
                    break
                else:
                    length_messages += len(history[index])
                    last_index = index
            history = history[last_index:]
            history.insert(0, {"role": "system", "content": prompt})
            print(history)
            async with ChatActionSender.record_voice(bot=bot, chat_id=message.chat.id, interval=2, initial_sleep=2):
                # action.record_voice(message.from_user.id, bot)
                await asyncio.sleep(0.5)
                x = AIGirlfriend(history)
                msg = await x.get_response(message_text)
                file_name = await conver_to_audio(msg, voice_id)
                # await bot.send_chat_action(message.from_user.id, ChatAction.RECORD_VOICE)

                audio_path_ogg = file_name.split(".")[0] + '.ogg'
                subprocess.run(["ffmpeg", '-i', file_name, '-acodec', 'libopus', audio_path_ogg, '-y'])
                duration = (await message.answer_voice(voice=FSInputFile(audio_path_ogg))).voice.duration
                db.add_row(bot_id, message.from_user.id, "user", message_text)
                db.add_row(bot_id, message.from_user.id, "assistant", msg, duration)
                os.remove(audio_path_ogg)
                os.remove(file_name)
        else:

            rates = db.get_all_rates_by_bot_id(bot_id)
            price_per_minute = db.get_price_per_minute(bot_id)[0][0]

            await message.answer(f"Минута моего аудио-ответа стоит {price_per_minute}₽. "
                                 f"Твои сообщения на 100% бесплатные.\n\nКакой тариф выберешь?😉",
                                 reply_markup=client_markup.create_markup_choice_rate(rates, bot_id))
