import asyncio
import os
import config
from aiogram import Router, Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

import elevenlab
from dispatchers import dp_new_bot, polling_manager
from db_ import db
import markup.admin_markup as admin_markup
import replicas.replicas_main_bot as replicas
import FSM
from polling_manager import add_bot

commands_router = Router()


async def on_startup_load_bots(bot: Bot):
    bots = db.get_active_bots()
    for bot_ in bots:
        if bot_[3] == "запущен":
            for admin in config.ADMINS:
                try:
                    await bot.send_message(admin, f"Бот [{bot_[2]}] успешно запущен!")
                except:
                    pass
            db.update_status_bot(bot_[1], "запущен")
            await add_bot(bot_[1], dp_new_bot, polling_manager)


@commands_router.startup()
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    asyncio.create_task(on_startup_load_bots(bot))


@commands_router.message(CommandStart())
async def start(message: Message):

    if message.from_user.id in config.ADMINS:
        await message.answer("Привет!", reply_markup=admin_markup.create_start_markup())


@commands_router.message(FSM.FSMAdmin.get_count_minutes)
async def get_count_minutes(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data["msg_id"])
    await message.delete()
    count_minutes = message.text
    if count_minutes.isdigit():
        msg = await message.answer("Отлично, теперь пришли мне цену на данный тариф", reply_markup=admin_markup.create_markup_rate_back())
        data["msg_id"] = msg.message_id
        data["count_minutes"] = count_minutes
        await state.set_state(FSM.FSMAdmin.get_price)
    else:
        msg = await message.answer("Количество минут должно быть целым числом, повтори ввод", reply_markup=admin_markup.create_markup_rate_back())
        data["msg_id"] = msg.message_id
    await state.set_data(data)


@commands_router.message(FSM.FSMAdmin.get_price)
async def get_price_rate(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data["msg_id"])
    await message.delete()
    price = message.text
    if price.isdigit():
        count_minutes = data["count_minutes"]
        bot_id = data["token"].split(":")[0]
        db.add_rate(bot_id, count_minutes, price)
        rates = db.get_all_rates_by_bot_id(bot_id)
        current_rates = ""
        for rate in rates:
            current_rates += f"{rate[2]} минут - {rate[3]}₽\n"
        await message.answer(f"Успешно добавил тариф!\n\nТекущие тарифы:\n{current_rates}", reply_markup=admin_markup.create_markup_rates(bot_id))
        await state.set_state(FSM.FSMAdmin.get_rates)
    else:
        msg = await message.answer("Количество минут должно быть целым числом, повтори ввод", reply_markup=admin_markup.create_markup_rate_back())
        data["msg_id"] = msg.message_id
        await state.set_data(data)


@commands_router.message(FSM.FSMAdmin.get_new_count_minutes)
async def get_new_count_minutes(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data["msg_id"])
    await message.delete()
    count_minutes = message.text
    if count_minutes.isdigit():
        msg = await message.answer("Отлично, теперь пришли мне новую цену на данный тариф")
        data = await state.get_data()
        data["msg_id"] = msg.message_id
        data["count_minutes"] = count_minutes
        await state.set_state(FSM.FSMAdmin.get_new_price)
    else:
        msg = await message.answer("Количество минут должно быть целым числом, повтори ввод")
        data["msg_id"] = msg.message_id
    await state.set_data(data)


@commands_router.message(FSM.FSMAdmin.get_new_price)
async def get_new_price(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data["msg_id"])
    await message.delete()
    price = message.text
    if price.isdigit():
        data = await state.get_data()
        count_minutes = data["count_minutes"]
        bot_id = data["token"].split(":")[0]
        rate_id = data["edit_rate_id"]
        db.update_rate(rate_id, count_minutes, price)
        rates = db.get_all_rates_by_bot_id(bot_id)
        current_rates = ""
        for rate in rates:
            current_rates += f"{rate[2]} минут - {rate[3]}₽\n"
        await message.answer(f"Успешно обновил тариф!\n\nТекущие тарифы:\n{current_rates}", reply_markup=admin_markup.create_markup_rates(bot_id))
        await state.set_state(FSM.FSMAdmin.get_rates)
    else:
        msg = await message.answer("Количество минут должно быть целым числом, повтори ввод")
        data["msg_id"] = msg.message_id
        await state.set_data(data)


@commands_router.message(FSM.FSMAdmin.get_prompt)
async def get_prompt(message: Message, state: FSMContext):

    await state.set_data({"prompt": message.text})
    await message.answer("""🤖️ Чтобы подключить нового персонажа, мне нужен токен
➀ Перейдите в @BotFather

➁ Отправьте в @BotFather команду - /newbot

➂ Придумайте название и юзернейм для вашего бота, например: "Новости" | @newsbot

➃ @BotFather выдаст вам токен бота, пример токена: 5827254996:AAEBu9108achvHoWvPmvr6kueDgmFpJMjHo

➄ Пришлите токен нового бота сюда ☟""")
    await state.set_state(FSM.FSMAdmin.get_token_bot)


@commands_router.message(FSM.FSMAdmin.get_voice)
async def get_voice(message: Message, state: FSMContext, bot: Bot):
    if message.voice is not None:

        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_name = f"{file_id}.mp3"
        await bot.download_file(file_path, file_name)

        data = await state.get_data()
        token = data["token"]
        bot_id = token.split(":")[0]

        # voice_id = elevenlab.add_voice(f"voice_{bot_id}", file_name)
        voice_id = "123"
        os.remove(file_name)
        await state.set_data(data)

        prompt = data["prompt"]
        token_yoomoney = data["token_yoomoney"]
        result, username, bot_id = await add_bot(token, dp_new_bot, polling_manager)
        if bot_id:
            db.add_bot(bot_id, token, username, "запущен", prompt, voice_id, token_yoomoney)
        await message.answer(result)
        await state.set_state(FSM.FSMAdmin.get_rates)
        await message.answer("Теперь давай настроим тарифы", reply_markup=admin_markup.create_markup_rates(bot_id))

        #     # db.add_row(bot_id, message.from_user.id, "system", prompt)
        # await state.clear()


@commands_router.message(FSM.FSMAdmin.get_token_bot)
async def get_token_bot(message: Message, state: FSMContext):
    data = await state.get_data()
    if len(message.text.split(":")) == 2 and message.text.split(":")[0].isdigit():
        data["token"] = message.text

        await state.set_data(data)
        await state.set_state(FSM.FSMAdmin.get_yoomoney_token)
        await message.answer("Пришли мне токен yoomoney для персонажа")

    else:
        await message.answer("Токен не прошел проверку, повтори попытку")


@commands_router.message(FSM.FSMAdmin.get_yoomoney_token)
async def get_yoomoney_token(message: Message, state: FSMContext):
    data = await state.get_data()
    data["token_yoomoney"] = message.text
    await state.set_data(data)
    await message.answer("Пришли мне голос для персонажа")
    await state.set_state(FSM.FSMAdmin.get_voice)


@commands_router.message(FSM.FSMAdmin.get_new_prompt)
async def get_new_prompt(message: Message, state: FSMContext):
    if message.text == replicas.cancel:
        data = await state.get_data()
        bots = db.get_bots()
        for bot in bots:
            if bot[0] == data['bot_id']:
                msg = f"<i>Изменение промпта отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
    else:
        data = await state.get_data()
        db.update_prompt(data["bot_id"], message.text)
        # await message.answer("Успешно изменил промпт", reply_markup=admin_markup.create_start_markup())
        bots = db.get_bots()
        for bot in bots:
            if bot[0] == data['bot_id']:
                msg = f"<i>Промпт успешно изменен</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
    await state.clear()
    await message.answer('Главное меню', reply_markup=admin_markup.create_start_markup())


@commands_router.message(FSM.FSMAdmin.get_new_yoomoney_token)
async def get_new_yoomoney_token(message: Message, state: FSMContext):
    msg = await message.answer('Загрузка', reply_markup=admin_markup.create_start_markup())
    await msg.delete()
    if message.text == replicas.cancel:
        data = await state.get_data()
        bots = db.get_bots()
        for bot in bots:
            if bot[0] == data['bot_id']:
                msg = f"<i>Изменение токена yoomoney отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]),
                                     parse_mode='HTML')
    else:
        data = await state.get_data()
        db.update_yoomoney(data["bot_id"], message.text)
        # await message.answer("Успешно изменил токен yoomoney", reply_markup=admin_markup.create_start_markup())
        bots = db.get_bots()
        for bot in bots:
            if bot[0] == data['bot_id']:
                msg = f"<i>Токен yoomoney успешно изменен</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
    await state.clear()
    await message.answer('Главное меню', reply_markup=admin_markup.create_start_markup())


@commands_router.message(FSM.FSMAdmin.get_new_voice)
async def get_new_voice(message: Message, state: FSMContext, bot: Bot):
    if message.text == replicas.cancel:
        data = await state.get_data()
        bots = db.get_bots()
        for bot in bots:
            if bot[0] == data['bot_id']:
                msg = f"<i>Изменение голоса отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]),
                                     parse_mode='HTML')
        await state.clear()
    if message.voice is not None:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        file_name = f"{file_id}.mp3"
        await bot.download_file(file_path, file_name)

        data = await state.get_data()
        bot_id = data["bot_id"]

        voice_id = elevenlab.add_voice(f"voice_{bot_id}", file_name)
        db.update_voice_id(bot_id, voice_id)
        os.remove(file_name)
        # await message.answer("Успешно изменил voice id персонажа", reply_markup=admin_markup.create_start_markup())
        bots = db.get_bots()
        for bot in bots:
            if bot[0] == data['bot_id']:
                msg = f"<i>Голос персонажа успешно изменен</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
        await state.clear()
    await message.answer('Главное меню', reply_markup=admin_markup.create_start_markup())


@commands_router.message()
async def all_messages(message: Message, bot: Bot, state: FSMContext):
    if message.text == replicas.create_character:
        await message.answer("Пришли мне промпт нового персонажа")
        await state.set_state(FSM.FSMAdmin.get_prompt)

    elif message.text == replicas.my_character:
        bots = db.get_bots()
        if len(bots) == 0:
            await message.answer("У вас нет персонажей")
            return

        for bot in bots:
            msg = f"[{bot[3]}] - @{bot[2]}\n"
            await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]))


# async def set_commands(bot: Bot):
#     commands = [
#         BotCommand(
#             command="add_bot",
#             description="add bot, usage '/add_bot 123456789:qwertyuiopasdfgh'",
#         ),
#         BotCommand(
#             command="stop_bot",
#             description="stop bot, usage '/stop_bot 123456789'",
#         ),
#     ]
#
#     await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())


# async def on_bot_startup(bot: Bot):
#     await set_commands(bot)
#     await bot.send_message(chat_id=ADMIN_ID, text="Bot started!")
#
#
# async def on_bot_shutdown(bot: Bot):
#     await bot.send_message(chat_id=ADMIN_ID, text="Bot shutdown!")
#
#
# async def on_startup(bots: List[Bot]):
#     for bot in bots:
#         await on_bot_startup(bot)
#
#
# async def on_shutdown(bots: List[Bot]):
#     for bot in bots:
#         await on_bot_shutdown(bot)
#
