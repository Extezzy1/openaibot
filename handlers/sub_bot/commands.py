import asyncio
import datetime
import os
import subprocess

from aiogram import Router, Bot, flags
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


@commands_router.message(CommandStart())
async def start(message: Message, bot: Bot):
    bot_id = (await bot.get_me()).id
    if not db.exist_user(bot_id, message.from_user.id):
        db.add_user(bot_id, message.from_user.id, message.from_user.username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    prompt = db.get_prompt(bot_id)[0][0]
    if not len(db.get_history_by_user_id(bot_id, message.from_user.id)):
        db.add_row(bot_id, message.from_user.id, "system", prompt)
    await message.answer("Привет! Напиши мне что-нибудь")


@commands_router.message(flags={"long_operation": "record_voice"})
async def all_messages(message: Message, bot: Bot):
    message_text = message.text
    bot_id = (await bot.get_me()).id
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



