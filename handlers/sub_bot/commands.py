import asyncio
import datetime
import os
import subprocess

from aiogram import Router, Bot, flags, Dispatcher
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender, ChatActionMiddleware

import config
import markup.client_markup as client_markup
from elevenlab import conver_to_audio
from openai_ import AIGirlfriend
from db_ import db
from middlewares import ChatActionMiddleware

commands_router = Router()
commands_router.message.middleware.register(ChatActionMiddleware())


async def check_media_and_mailing(bot: Bot):
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
            elif last_message_time + datetime.timedelta(days=2) < datetime.datetime.now() and user[3] == 0:
                try:
                    db.update_mailing(bot_id, user[0], "is_send_2_day")
                    await bot.send_message(user[0], config.message_mailing_2_day)
                except Exception as ex:
                    print(ex)
            elif last_message_time + datetime.timedelta(days=3) < datetime.datetime.now() and user[4] == 0:
                try:
                    db.update_mailing(bot_id, user[0], "is_send_3_day")
                    await bot.send_message(user[0], config.message_mailing_3_day)
                except Exception as ex:
                    print(ex)
            elif last_message_time + datetime.timedelta(days=7) < datetime.datetime.now() and user[5] == 0:
                try:
                    db.update_mailing(bot_id, user[0], "is_send_7_day")
                    await bot.send_message(user[0], config.message_mailing_7_day)
                except Exception as ex:
                    print(ex)

        await asyncio.sleep(30)



async def on_bot_startup(dispatcher: Dispatcher, bot: Bot):
    asyncio.create_task(check_media_and_mailing(bot))


@commands_router.message(CommandStart())
async def start(message: Message, bot: Bot):
    bot_id = (await bot.get_me()).id
    if not db.exist_user(bot_id, message.from_user.id):
        db.add_user(bot_id, message.from_user.id, message.from_user.username, message.from_user.full_name)
    else:
        db.update_last_message_time(bot_id, message.from_user.id)

    prompt = db.get_prompt(bot_id)[0][0]
    if not len(db.get_history_by_user_id(bot_id, message.from_user.id)):
        db.add_row(bot_id, message.from_user.id, "system", prompt)
    start_message = db.get_start_message(bot_id)[0]
    if start_message[0] is not None:

        if start_message[1] is not None:
            await message.answer_photo(photo=start_message[1], caption=start_message[0])
        else:
            await message.answer(start_message[0])


@commands_router.message(flags={"long_operation": "record_voice"})
async def all_messages(message: Message, bot: Bot):

    message_text = message.text
    bot_id = (await bot.get_me()).id
    db.update_last_message_time(bot_id, message.from_user.id)
    voice_id = db.get_voice_id(bot_id)[0][0]
    total_length = db.get_total_lenght_by_user(message.from_user.id, bot_id)[0][0]
    user_minutes = db.get_minutes_by_user(bot_id, message.from_user.id)

    if total_length < user_minutes * 60:

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
            file_name = conver_to_audio(msg, voice_id)
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
                             reply_markup=client_markup.create_markup_choice_rate(rates))



