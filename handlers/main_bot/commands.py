import asyncio
import os
import random

from aiogram.utils.media_group import MediaGroupBuilder

import config
from aiogram import Router, Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
import elevenlab
import utils
from dispatchers import dp_new_bot, polling_manager
from db_ import db
import markup.admin_markup as admin_markup
import replicas.replicas_main_bot as replicas
import FSM
from polling_manager import add_bot
import datetime

alphabet_lower = [chr(i) for i in range(97, 123)]
alphabet_upper = [chr(i) for i in range(65, 91)]
alphabet_numbers = [chr(i) for i in range(48, 58)]
alphabet = alphabet_lower + alphabet_upper + alphabet_numbers
commands_router = Router()


def validate_date(date):
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d %H:%M")
        return True
    except Exception as ex:
        print(ex)
        return False


async def on_startup_load_bots(bot: Bot):

    bots = db.get_active_bots()
    for bot_ in bots:
        if bot_[3] == "запущен":
            # for admin in config.ADMINS:
            #     try:
            #         await bot.send_message(admin, f"Бот [{bot_[2]}] успешно запущен!")
            #     except:
            #         pass
            db.update_status_bot(bot_[1], "запущен")
            await add_bot(bot_[1], dp_new_bot, polling_manager)

    while True:
        bots = db.get_active_bots()
        for bot_ in bots:
            mailing = db.get_mailing(bot_[0])
            if len(mailing) > 0:
                print(mailing)
                if mailing[0][5] == 1:
                    await bot.send_message(mailing[0][6], f"Рассылка успешно окончена, сообщение отправлено {mailing[0][7]} пользователям!", reply_markup=admin_markup.create_start_markup())
                    db.delete_mailing(mailing[0][0])
                else:
                    if mailing[0][7] != 0:
                        print(mailing[0][6], mailing[0][9])
                        await bot.edit_message_text(text=f"Начинаю рассылку... {mailing[0][7]}/{mailing[0][8]}", chat_id=int(mailing[0][6]), message_id=int(mailing[0][9]))
                        # await bot.send_message(text=f"Начинаю рассылку... {mailing[0][7]}/{mailing[0][8]}", chat_id=int(mailing[0][6]))
        feedback_messages = db.get_feedback_messages_not_send()
        for message in feedback_messages:
            bot_username = db.get_bot_username(message[2])
            print(message)
            for admin in config.ADMINS:
                if message[4] is not None:
                    await bot.send_photo(chat_id=admin, photo=FSInputFile(message[4]), caption=message[3])
                elif message[5] is not None:
                    await bot.send_document(chat_id=admin, document=FSInputFile(message[5]), caption=message[3])
                elif message[6] is not None:
                    await bot.send_video(chat_id=admin, video=FSInputFile(message[6]), caption=message[3])
                else:
                    await bot.send_message(admin, message[3])
                user = db.get_user_by_user_id(message[1], message[2])[0]
                if user[3] is None:
                    await bot.send_message(admin, f'[{bot_username}]\n☝️☝️☝️\nПользователь <a href="tg://user?id={message[1]}">{user[13]}</a> [ID: {message[1]}] оставил вопрос',
                                       reply_markup=admin_markup.create_markup_feedback(message[0], message[1], message[2]))
                else:
                    await bot.send_message(admin, f'[{bot_username}]\n☝️☝️☝️\nПользователь @{user[3]}, <a href="tg://user?id={message[1]}">{user[13]}</a> [ID: {message[1]}] оставил вопрос',
                                       reply_markup=admin_markup.create_markup_feedback(message[0], message[1], message[2]))
                # await bot.send_message(admin, f'☝️☝️☝️\nПользователь {user[3]}, <a href="{message.from_user.url}">{user[13]}</a> [ID: {message[1]}] оставил вопрос',
                #                        reply_markup=admin_markup.create_markup_feedback(message[0], message[1], message[2]))
                db.update_status_feedback_message("is_send", 1)
            if message[4] is not None:
                os.remove(message[4])
            elif message[5] is not None:
                os.remove(message[5])
            elif message[6] is not None:
                os.remove(message[6])

        successfull_subscribes = db.get_successfull_subscribe()
        for subscribe in successfull_subscribes:
            db.update_is_send_admin_about_new_subscribe(subscribe[0])
            for admin in config.ADMINS:
                try:

                    user_id = subscribe[1]
                    bot_id = subscribe[4]
                    bot_username = db.get_bot_username(bot_id)
                    rate_id = subscribe[12]
                    user = db.get_user_by_user_id(user_id, bot_id)[0]
                    count_minutes, price, price_dollar = db.get_amount_by_rate_id(rate_id)
                    username = f"@{user[3]}, " if user[3] is not None else ""
                    await bot.send_message(chat_id=admin, text=f"[{bot_username}]\n💰 Новая подписка\n\nПользователь: {username}{user[13]} (ID: {user_id})\n"
                                                               f"Тариф: {count_minutes} минут - {price}₽ / {price_dollar}$\n"
                                                               f"Сумма оплаты: {subscribe[3]}₽")
                except:
                    pass

        await asyncio.sleep(0.5)


@commands_router.startup()
async def on_startup(dispatcher: Dispatcher, bot: Bot):
    asyncio.create_task(on_startup_load_bots(bot))


@commands_router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in config.ADMINS:
        print(message.from_user.url)
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
        msg = await message.answer(f"Отлично, теперь пришли мне цену на данный тариф в долларах", reply_markup=admin_markup.create_markup_rate_back())
        data["price"] = price
        data["msg_id"] = msg.message_id
        await state.set_state(FSM.FSMAdmin.get_price_dollar)
    else:
        msg = await message.answer("Количество минут должно быть целым числом, повтори ввод", reply_markup=admin_markup.create_markup_rate_back())
        data["msg_id"] = msg.message_id
    await state.set_data(data)


@commands_router.message(FSM.FSMAdmin.get_price_dollar)
async def get_price_rate_dollar(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data["msg_id"])
    await message.delete()
    price_dollar = message.text
    if price_dollar.isdigit():
        count_minutes = data["count_minutes"]
        price = data["price"]
        bot_id = data["token"].split(":")[0]
        db.add_rate(bot_id, count_minutes, price, price_dollar)
        rates = db.get_all_rates_by_bot_id(bot_id)
        current_rates = ""
        for rate in rates:
            current_rates += f"{rate[2]} минут - {rate[3]}₽ / {rate[4]}$\n"
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
        msg = await message.answer("Отлично, теперь пришли мне новую цену на данный тариф <b>в долларах</b>")
        data["msg_id"] = msg.message_id
        data["price"] = price
        await state.set_state(FSM.FSMAdmin.get_new_dollar_price)
    else:
        msg = await message.answer("Цена должна быть целым числом, повтори ввод")
        data["msg_id"] = msg.message_id
    await state.set_data(data)


@commands_router.message(FSM.FSMAdmin.get_new_dollar_price)
async def get_new_price_dollar(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await bot.delete_message(message.from_user.id, data["msg_id"])
    await message.delete()
    dollar_price = message.text
    if dollar_price.isdigit():
        count_minutes = data["count_minutes"]
        price = data["price"]
        bot_id = data["token"].split(":")[0]
        rate_id = data["edit_rate_id"]
        db.update_rate(rate_id, count_minutes, price, dollar_price)
        rates = db.get_all_rates_by_bot_id(bot_id)
        current_rates = ""
        for rate in rates:
            current_rates += f"{rate[2]} минут - {rate[3]}₽ / {rate[4]}$\n"
        await message.answer(f"Успешно обновил тариф!\n\nТекущие тарифы:\n{current_rates}", reply_markup=admin_markup.create_markup_rates(bot_id))
        await state.set_state(FSM.FSMAdmin.get_rates)
    else:
        msg = await message.answer("Цена должна быть целым числом, повтори ввод")
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

        voice_id = elevenlab.add_voice(f"voice_{bot_id}", file_name)
        # voice_id = "123"
        os.remove(file_name)
        await state.set_data(data)

        prompt = data["prompt"]
        token_yoomoney = data["token_yoomoney"]
        price_per_minute = data["price_per_minute"]
        result, username, bot_id = await add_bot(token, dp_new_bot, polling_manager)
        if bot_id:
            db.add_bot(bot_id, token, username, "запущен", prompt, voice_id, token_yoomoney, price_per_minute)
        await message.answer(result)

        await message.answer("Теперь пришли мне текст стартового сообщения для персонажа")
        await state.set_state(FSM.FSMAdmin.get_start_text)

        #     # db.add_row(bot_id, message.from_user.id, "system", prompt)
        # await state.clear()


@commands_router.message(FSM.FSMAdmin.get_token_bot)
async def get_token_bot(message: Message, state: FSMContext):
    data = await state.get_data()
    if len(message.text.split(":")) == 2 and message.text.split(":")[0].isdigit():
        data["token"] = message.text

        await state.set_data(data)

        await state.set_state(FSM.FSMAdmin.get_price_per_minute)
        await message.answer("Пришли мне цену за одну минуту сообщения персонажа")

    else:
        await message.answer("Токен не прошел проверку, повтори попытку")


@commands_router.message(FSM.FSMAdmin.get_price_per_minute)
async def get_price_per_minute(message: Message, state: FSMContext):
    data = await state.get_data()
    data["price_per_minute"] = message.text
    await state.set_data(data)
    await state.set_state(FSM.FSMAdmin.get_yoomoney_token)
    bot_id = data["token"].split(":")[0]
    await message.answer(f"""Теперь необходимо:
1. Авторизоваться в Юмани под аккаунтом, на который будете принимать платежи
2. Перейти по ссылке - https://yoomoney.ru/transfer/myservices/http-notification
3. В поле "Куда отправлять (URL сайта)" ввести ссылку "http://194.147.148.34/payment/{bot_id}"
4. Поставить галочку в поле "Отправлять HTTP-уведомления
5. Нажать кнопку "Готово"
6. Прислать токен yoomoney для персонажа""")


@commands_router.message(FSM.FSMAdmin.get_yoomoney_token)
async def get_yoomoney_token(message: Message, state: FSMContext):
    data = await state.get_data()
    data["token_yoomoney"] = message.text
    await state.set_data(data)
    await message.answer("Пришли мне голос для персонажа")
    await state.set_state(FSM.FSMAdmin.get_voice)


@commands_router.message(FSM.FSMAdmin.get_start_photo)
async def get_start_photo(message: Message, state: FSMContext, bot: Bot):
    if message.photo is not None:
        data = await state.get_data()
        bot_id = data["token"].split(":")[0]
        photo = message.photo[-1].file_id
        file = await bot.get_file(photo)
        file_path = file.file_path
        await bot.download_file(file_path, f"media/{bot_id}_{file_path.split('/')[-1]}")
        await state.set_state(FSM.FSMAdmin.get_rates)
        await message.answer("Теперь давай настроим тарифы",
                                      reply_markup=admin_markup.create_markup_rates(bot_id))

    else:
        await message.answer("Я жду картинку (не забудь поставить галочку на пункте «Сжать изображение»)")


@commands_router.message(FSM.FSMAdmin.get_new_start_photo)
async def get_new_start_photo(message: Message, state: FSMContext, bot: Bot):
    if message.photo is not None:
        data = await state.get_data()
        bot_id = data["bot_id"]
        photo = message.photo[-1].file_id
        file = await bot.get_file(photo)
        file_path = file.file_path
        await bot.download_file(file_path, f"media/{bot_id}_{file_path.split('/')[-1]}")
        await message.answer("Картинка обновиться в течении 15-30 секунд, ожидайте...",
                                      reply_markup=admin_markup.create_start_markup())
        await state.clear()
    else:
        await message.answer("Я жду картинку (не забудь поставить галочку на пункте «Сжать изображение»)")


@commands_router.message(FSM.FSMAdmin.get_text_answer_user)
async def get_text_answer_user(message: Message, bot: Bot, state: FSMContext):

    if message.text == replicas.cancel:
        await message.answer("<b>Действие отменено</b>")
    else:

        if message.text is None and message.photo is None and message.video is None and message.document is None:
            await message.answer(
                "Ответ должен содержать текст или медиа вложение, повторите ввод или отмените действие")
            return
        data = await state.get_data()
        message_id = data["message_id"]
        message_text = message.text
        photo, video, document = None, None, None
        if message.photo is not None:
            message_text = message.caption
            file = await bot.get_file(message.photo[-1].file_id)
            file_path = file.file_path
            photo = f"feedback_answer/{message_id}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, photo)
        elif message.video is not None:
            message_text = message.caption
            file = await bot.get_file(message.video.file_id)
            file_path = file.file_path
            video = f"feedback_answer/{message_id}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, video)
        elif message.document is not None:
            message_text = message.caption
            file = await bot.get_file(message.video.file_id)
            file_path = file.file_path
            document = f"feedback_answer/{message_id}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, document)
        db.update_answer_feedback(data["message_id"], message_text, photo=photo, video=video, document=document)
        await message.answer("Ответ успешно отправлен пользователю!")
    await state.clear()


@commands_router.message(FSM.FSMAdmin.get_title_promo)
async def get_text_promo(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        bot_id = data["bot_id"]
        promocodes = db.get_promocodes(bot_id)
        await message.answer(
            "<b>Настройка промокодов</b>\n\nВыберите промокод ниже для настройки или создайте новый",
            reply_markup=admin_markup.create_markup_promocodes(promocodes, bot_id))
        await state.clear()
    else:
        data["title_promo"] = message.text
        await message.answer("Пришлите мне процент скидки", reply_markup=admin_markup.create_cancel_markup())
        await state.set_data(data)
        await state.set_state(FSM.FSMAdmin.get_discount_percent)


@commands_router.message(FSM.FSMAdmin.get_discount_percent)
async def get_discount_percent(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        bot_id = data["bot_id"]
        promocodes = db.get_promocodes(bot_id)
        await message.answer(
            "<b>Настройка промокодов</b>\n\nВыберите промокод ниже для настройки или создайте новый",
            reply_markup=admin_markup.create_markup_promocodes(promocodes, bot_id))
        await state.clear()
    else:
        if message.text.isdigit():
            data["discount_percent"] = int(message.text)
            await message.answer("Пришлите мне общее количество активаций", reply_markup=admin_markup.create_cancel_markup())
            await state.set_data(data)
            await state.set_state(FSM.FSMAdmin.get_count_activation_total)
        else:
            await message.answer("Процент скидки должен быть целым числом, повторите ввод", reply_markup=admin_markup.create_cancel_markup())


@commands_router.message(FSM.FSMAdmin.get_count_activation_total)
async def get_count_activation_total(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        bot_id = data["bot_id"]
        promocodes = db.get_promocodes(bot_id)
        await message.answer(
            "<b>Настройка промокодов</b>\n\nВыберите промокод ниже для настройки или создайте новый",
            reply_markup=admin_markup.create_markup_promocodes(promocodes, bot_id))
        await state.clear()
    else:
        if message.text.isdigit():
            data["count_activation_total"] = int(message.text)
            await message.answer("Пришлите мне количество активаций на 1 человека", reply_markup=admin_markup.create_cancel_markup())
            await state.set_data(data)
            await state.set_state(FSM.FSMAdmin.get_count_activation_by_person)
        else:
            await message.answer("Количество активаций должно быть целым числом, повторите ввод", reply_markup=admin_markup.create_cancel_markup())


@commands_router.message(FSM.FSMAdmin.get_count_activation_by_person)
async def get_count_activation_by_person(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        bot_id = data["bot_id"]
        promocodes = db.get_promocodes(bot_id)
        await message.answer(
            "<b>Настройка промокодов</b>\n\nВыберите промокод ниже для настройки или создайте новый",
            reply_markup=admin_markup.create_markup_promocodes(promocodes, bot_id))
        await state.clear()
    else:
        if message.text.isdigit():
            data["count_activation_by_person"] = int(message.text)
            await message.answer("Пришлите мне дату окончания действия промокода в формате ГГГГ-ММ-ДД ЧЧ:ММ", reply_markup=admin_markup.create_cancel_markup())
            await state.set_data(data)
            await state.set_state(FSM.FSMAdmin.get_date_end)
        else:
            await message.answer("Количество активаций должно быть целым числом, повторите ввод", reply_markup=admin_markup.create_cancel_markup())


@commands_router.message(FSM.FSMAdmin.get_date_end)
async def get_date_end(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_id = data["bot_id"]
    if message.text == replicas.cancel:
        promocodes = db.get_promocodes(bot_id)
        await message.answer(
            "<b>Настройка промокодов</b>\n\nВыберите промокод ниже для настройки или создайте новый",
            reply_markup=admin_markup.create_markup_promocodes(promocodes, bot_id))

        await state.clear()
    else:
        if validate_date(message.text) or message.text == "0":
            bot_username = db.get_bot_username(bot_id)
            marks = [i[3] for i in db.get_marks(bot_id)]
            link = f"https://t.me/{bot_username}?start=" + "".join(
                [alphabet[random.randint(0, len(alphabet) - 1)] for i in range(10)])
            while link in marks:
                link = f"https://t.me/{bot_username}?start=" + "".join(
                    [alphabet[random.randint(0, len(alphabet) - 1)] for i in range(10)])
            db.add_promocode(bot_id, data["title_promo"], data["discount_percent"],
                             data["count_activation_total"], data["count_activation_by_person"], message.text, link)
            promocodes = db.get_promocodes(bot_id)
            await message.answer(
                f"<b>Успешно добавил промокод!</b>\n{link}\n\n<b>Настройка промокодов</b>\n\nВыберите промокод ниже для настройки или создайте новый",
                reply_markup=admin_markup.create_markup_promocodes(promocodes, bot_id))
            await state.clear()
            await state.set_data(data)
            await state.set_state(FSM.FSMAdmin.get_date_end)
        else:
            await message.answer("Дата должна быть в формате ГГГГ-ММ-ДД ЧЧ:ММ, повторите ввод", reply_markup=admin_markup.create_cancel_markup())


@commands_router.message(FSM.FSMAdmin.get_new_count_activation_total)
async def get_new_count_activation_total(message: Message, state: FSMContext):
    data = await state.get_data()
    promo_id = data["promo_id"]
    bot_id = data["bot_id"]
    if message.text == replicas.cancel:
        msg = utils.create_message_promo(promo_id)
        await message.answer(msg, reply_markup=admin_markup.create_markup_promocode(bot_id, promo_id))
        await state.clear()
    else:
        if message.text.isdigit():
            db.update_promocode(promo_id, "count_activation_total", message.text)
            msg = utils.create_message_promo(promo_id)
            await message.answer(msg, reply_markup=admin_markup.create_markup_promocode(bot_id, promo_id))
            await state.clear()
        else:
            await message.answer("Количество активаций должно быть целым числом, повторите ввод", reply_markup=admin_markup.create_cancel_markup())


@commands_router.message(FSM.FSMAdmin.get_new_count_activation_by_person)
async def get_new_count_activation_by_person(message: Message, state: FSMContext):
    data = await state.get_data()
    promo_id = data["promo_id"]
    bot_id = data["bot_id"]
    if message.text == replicas.cancel:
        msg = utils.create_message_promo(promo_id)
        await message.answer(msg, reply_markup=admin_markup.create_markup_promocode(bot_id, promo_id))
        await state.clear()
    else:
        if message.text.isdigit():
            db.update_promocode(promo_id, "count_activation_by_person", message.text)
            msg = utils.create_message_promo(promo_id)
            await message.answer(msg, reply_markup=admin_markup.create_markup_promocode(bot_id, promo_id))
            await state.clear()
        else:
            await message.answer("Количество активаций должно быть целым числом, повторите ввод", reply_markup=admin_markup.create_cancel_markup())


@commands_router.message(FSM.FSMAdmin.get_new_date_end)
async def get_new_date_end(message: Message, state: FSMContext):
    data = await state.get_data()
    promo_id = data["promo_id"]
    bot_id = data["bot_id"]
    if message.text == replicas.cancel:
        msg = utils.create_message_promo(promo_id)
        await message.answer(msg, reply_markup=admin_markup.create_markup_promocode(bot_id, promo_id))
        await state.clear()
    else:
        if message.text.isdigit():
            db.update_promocode(promo_id, "date_end", message.text)
            msg = utils.create_message_promo(promo_id)
            await message.answer(msg, reply_markup=admin_markup.create_markup_promocode(bot_id, promo_id))
            await state.clear()
        else:
            await message.answer("Дата должна быть в формате ГГГГ-ММ-ДД ЧЧ:ММ, повторите ввод", reply_markup=admin_markup.create_cancel_markup())


@commands_router.message(FSM.FSMAdmin.get_new_start_text)
async def get_new_start_text(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        bots = db.get_bots()
        for bot in bots:
            if str(bot[0]) == data['bot_id']:
                msg = f"<i>Изменение стартового сообщения отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
        await state.clear()
    else:
        bot_id = data["bot_id"]
        db.update_start_text(bot_id, message.text)
        await message.answer("Добавляем картинку для стартового сообщения?", reply_markup=admin_markup.create_markup_edit_start_photo())


@commands_router.message(FSM.FSMAdmin.get_title_pay_type)
async def get_title_pay_type(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        bots = db.get_bots()
        for bot in bots:
            if str(bot[0]) == data['bot_id']:
                msg = f"<i>Добавление нового способа оплаты отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
        await state.clear()
    else:
        data["title"] = message.text
        await state.set_state(FSM.FSMAdmin.get_description_pay_type)
        await state.set_data(data)
        await message.answer("Теперь пришлите мне описание способа оплаты", reply_markup=admin_markup.create_cancel_markup())


@commands_router.message(FSM.FSMAdmin.get_description_pay_type)
async def get_description_pay_type(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        data = await state.get_data()
        bots = db.get_bots()
        for bot in bots:
            if str(bot[0]) == data['bot_id']:
                msg = f"<i>Добавление нового способа оплаты отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
        await state.clear()
    else:
        title = data["title"]
        description = message.text
        db.add_pay_type(data["bot_id"], title, description)
        await state.clear()
        pay_types = db.get_pay_types(data["bot_id"])
        await message.answer("Успешно добавил новый способ оплаты", reply_markup=admin_markup.create_markup_manual_pay(data["bot_id"], pay_types))


@commands_router.message(FSM.FSMAdmin.get_new_title_pay_type)
async def get_new_title_pay_type(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        pay_type = db.get_pay_type_by_id(data["pay_id"])
        await message.answer(f"<b>Название</b>: {pay_type[2]}\n\n<b>Описание</b>: {pay_type[3]}",
                                         reply_markup=admin_markup.create_markup_edit_manual_pay_type(pay_type[0],
                                                                                                      pay_type[1], pay_type[4]))
        await state.clear()
    else:
        name = message.text
        db.update_pay_type(data["pay_id"], 'name', name)
        pay_type = db.get_pay_type_by_id(data["pay_id"])
        await message.answer(f"<b>Успешно изменил наименование способа оплаты</b>\n\n<b>Название</b>: {pay_type[2]}\n\n<b>Описание</b>: {pay_type[3]}",
                                         reply_markup=admin_markup.create_markup_edit_manual_pay_type(pay_type[0],
                                                                                                      pay_type[1], pay_type[4]))
        await state.clear()


@commands_router.message(FSM.FSMAdmin.get_new_description_pay_type)
async def get_new_description_pay_type(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text == replicas.cancel:
        pay_type = db.get_pay_type_by_id(data["pay_id"])
        await message.answer(f"<b>Название</b>: {pay_type[2]}\n\n<b>Описание</b>: {pay_type[3]}",
                                         reply_markup=admin_markup.create_markup_edit_manual_pay_type(pay_type[0],
                                                                                                      pay_type[1], pay_type[4]))
        await state.clear()
    else:
        description = message.text
        db.update_pay_type(data["pay_id"], "description", description)
        pay_type = db.get_pay_type_by_id(data["pay_id"])
        await message.answer(f"<b>Успешно изменил описание способа оплаты</b>\n\n<b>Название</b>: {pay_type[2]}\n\n<b>Описание</b>: {pay_type[3]}",
                                         reply_markup=admin_markup.create_markup_edit_manual_pay_type(pay_type[0],
                                                                                                      pay_type[1], pay_type[4]))
        await state.clear()


@commands_router.message(FSM.FSMAdmin.get_start_text)
async def get_start_text(message: Message, state: FSMContext):
    data = await state.get_data()
    bot_id = data["token"].split(":")[0]
    db.update_start_text(bot_id, message.text)
    await message.answer("Добавляем картинку для стартового сообщения?", reply_markup=admin_markup.create_markup_add_start_photo())


@commands_router.message(FSM.FSMAdmin.get_mark_name)
async def get_mark_name(message: Message, state: FSMContext):
    name = message.text
    data = await state.get_data()
    bot_id = data["bot_id"]
    bot_username = db.get_bot_username(bot_id)
    link = f"https://t.me/{bot_username}?start=" + "".join([alphabet[random.randint(0, len(alphabet) - 1)] for i in range(10)])
    db.add_mark(bot_id, name, link)
    marks = db.get_marks(bot_id)
    await message.answer("Успешно добавил новую метку\n\nНастройка системы UTM меток\n\n"
                         "Выберите UTM метку ниже или создайте новую",
                         reply_markup=admin_markup.create_markup_choice_marks(bot_id, marks))
    await state.clear()


@commands_router.message(FSM.FSMAdmin.get_new_prompt)
async def get_new_prompt(message: Message, state: FSMContext):
    if message.text == replicas.cancel:
        data = await state.get_data()
        bots = db.get_bots()
        for bot in bots:
            if str(bot[0]) == str(data['bot_id']):
                msg = f"<i>Изменение промпта отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
    else:
        data = await state.get_data()
        db.update_prompt(data["bot_id"], message.text)
        # await message.answer("Успешно изменил промпт", reply_markup=admin_markup.create_start_markup())
        bots = db.get_bots()
        for bot in bots:
            if str(bot[0]) == str(data['bot_id']):
                msg = f"<i>Промпт успешно изменен</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
    await state.clear()
    await message.answer('Главное меню', reply_markup=admin_markup.create_start_markup())


@commands_router.message(FSM.FSMAdmin.get_new_price_per_minute)
async def get_new_price_per_minute(message: Message, state: FSMContext):
    if message.text == replicas.cancel:
        data = await state.get_data()
        bots = db.get_bots()
        for bot in bots:
            if str(bot[0]) == str(data['bot_id']):
                msg = f"<i>Изменение токена yoomoney отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]),
                                     parse_mode='HTML')
    else:
        data = await state.get_data()
        db.update_price_per_minute(data["bot_id"], message.text)
        # await message.answer("Успешно изменил токен yoomoney", reply_markup=admin_markup.create_start_markup())
        bots = db.get_bots()
        for bot in bots:
            if str(bot[0]) == str(data['bot_id']):
                msg = f"<i>Цена за минуту сообщения успешна изменена</i>\n\n[{bot[3]}] - @{bot[2]}\n"
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
            if str(bot[0]) == str(data['bot_id']):
                msg = f"<i>Изменение токена yoomoney отменено</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]),
                                     parse_mode='HTML')
    else:
        data = await state.get_data()
        db.update_yoomoney(data["bot_id"], message.text)
        # await message.answer("Успешно изменил токен yoomoney", reply_markup=admin_markup.create_start_markup())
        bots = db.get_bots()
        for bot in bots:
            if str(bot[0]) == str(data['bot_id']):
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
            if str(bot[0]) == str(data['bot_id']):
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
            if str(bot[0]) == str(data['bot_id']):
                msg = f"<i>Голос персонажа успешно изменен</i>\n\n[{bot[3]}] - @{bot[2]}\n"
                await message.answer(msg, reply_markup=admin_markup.create_markup_start_stop_bot(bot[3], bot[0]), parse_mode='HTML')
        await state.clear()
    await message.answer('Главное меню', reply_markup=admin_markup.create_start_markup())


@commands_router.message(FSM.FSMAdmin.get_text)
async def get_text_mailing(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if message.text == replicas.send:
        await message.answer("Выбери тип рассылки", reply_markup=admin_markup.create_markup_mailing_type())
    elif message.text in (replicas.mailing_all, replicas.mailing_without_subscribe):
        text = data["text"]
        photo = data.get("photo", None)
        video = data.get("video", None)
        document = data.get("document", None)
        photo_path = None
        video_path = None
        document_path = None
        if photo is not None:
            file = await bot.get_file(photo)
            file_path = file.file_path
            photo_path = f"mailing/{data['bot_id']}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, photo_path)
        elif video is not None:
            file = await bot.get_file(video)
            file_path = file.file_path
            video_path = f"mailing/{data['bot_id']}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, video_path)
        elif document is not None:
            file = await bot.get_file(document)
            file_path = file.file_path
            document_path = f"mailing/{data['bot_id']}_{file_path.split('/')[-1]}"
            await bot.download_file(file_path, document_path)

        # photos_result = []
        # for photo in photos:

        # photos_result = ";".join(photos_result) if len(photos_result) > 0 else None
        if message.text == replicas.mailing_all:
            type_ = "all"
        else:
            type_ = "without_subscribe"
        msg = await message.answer("Начинаю рассылку...")
        print(msg)
        db.add_mailing(data["bot_id"], text, photo_path, video_path, document_path, type_, message.from_user.id, msg.message_id)
        await state.clear()
    elif message.text == replicas.cancel_mailing:
        await message.answer("Главное меню", reply_markup=admin_markup.create_start_markup())
        await state.clear()
        # status = db.get_status_bot(data["bot_id"])
        # await message.answer(f"[{status}] - {db.get_bot_token(data['bot_id'])}", reply_markup=admin_markup.create_markup_start_stop_bot(status, data["bot_id"]))
    elif message.text == replicas.show_message:

        text = data.get("text", "")
        photo = data.get("photo", None)
        video = data.get("video", None)
        document = data.get("document", None)
        if photo is not None:
            await message.answer_photo(photo=photo, caption=text)
        elif video is not None:
            await message.answer_video(video=video, caption=text)
        elif document is not None:
            await message.answer_document(document=document, caption=text)
        else:
            await message.answer(text)
        # if len(photos) > 0:
        #     if len(photos) == 1:
        #         await message.answer_photo(photo=photos[0], caption=text)
        #     else:
        #         media_group = MediaGroupBuilder(caption=text)
        #         for photo in photos:
        #             media_group.add_photo(media=photo)
        #         await message.answer_media_group(media_group.build())

    # elif message.text == replicas.add_photo:
    #     await message.answer("Пришлите мне картинки для рассылки (не забудьте поставить галочку «Сжать изображение» при отправке)", reply_markup=admin_markup.create_markup_mailing_photo())
    #     await state.set_state(FSM.FSMAdmin.get_photo)
    else:
        text = message.html_text
        if message.photo is not None:
            data["photo"] = message.photo[-1].file_id
        elif message.video is not None:
            data["video"] = message.video.file_id
        elif message.document is not None:
            data["document"] = message.document.file_id
        data["text"] = text
        await state.set_data(data)
        await message.answer("Записал текст рассылки!", reply_markup=admin_markup.create_markup_mailing())


@commands_router.message(FSM.FSMAdmin.get_photo)
async def get_photo_mailing(message: Message, state: FSMContext):
    if message.text == replicas.end_add_photo:
        await message.answer("Остановил добавление картинок!", reply_markup=admin_markup.create_markup_mailing())
        await state.set_state(FSM.FSMAdmin.get_text)
    if message.photo is not None:
        data = await state.get_data()
        if not data.get("photos", False):
            data["photos"] = []
        data["photos"].append(message.photo[-1].file_id)
        await state.set_data(data)

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
