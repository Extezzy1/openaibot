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
import markup.client_markup as client_markup
from elevenlab import conver_to_audio
from openai_ import AIGirlfriend
from db_ import db
from payment import wallet
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
    # if total_length < 60:

    history = db.get_history_by_user_id(bot_id, message.from_user.id)
    # async with ChatActionSender.record_voice(message.from_user.id, bot):
    # await bot.send_chat_action(message.from_user.id, ChatAction.RECORD_VOICE)

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
    # else:
    #     url, bill = wallet.create_payment(3)
    #     await message.answer("Бесплатная минута закончилась, оплатите подписку!", reply_markup=client_markup.create_markup_payment(url, bill))
    #


