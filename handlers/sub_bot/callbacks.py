from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import FSM
import config
from payment import Payment
import markup.client_markup as client_markup
from db_ import db

callbacks_router = Router()


@callbacks_router.callback_query(F.data.startswith("payment_"))
async def payment_successful(callback: CallbackQuery, state: FSMContext):

    callback_data_split = callback.data.split("_")
    promo_id = callback_data_split[-3]
    rate_id = callback_data_split[-2]
    bill_pay_type_id = callback_data_split[-1]
    # if bill_pay_type_id.isdigit():
    # Оплата полуавтомат
    bot_id, _ = db.get_count_minutes_by_rate(int(rate_id))[0]
    await callback.message.answer("Пришли мне скриншот или документ об успешной оплате", reply_markup=client_markup.create_markup_cancel())
    await state.set_state(FSM.FSMUser.get_photo_document_pay)
    await state.set_data({"promo_id": promo_id, "rate_id": rate_id, "pay_type_id": bill_pay_type_id, "bot_id": bot_id})
    # else:
    #     # Оплата юмани
    #     yoomoney_token = db.get_yoomoney_token(rate_id)[0][0]
    #     mark_id = db.get_mark_id_by_user_id(callback.from_user.id)
    #     wallet = Payment(config.yoomoney_wallet, yoomoney_token)
    #     status, amount = wallet.check_payment(bill_pay_type_id)
    #     if status == 'Оплачено':
    #         await callback.message.answer("Успешно оплачено!")
    #         bot_id, count_minutes = db.get_count_minutes_by_rate(rate_id)[0]
    #         db.add_minutes(callback.from_user.id, bot_id, count_minutes)
    #         db.add_payment(bill_pay_type_id, callback.from_user.id, bot_id, amount, mark_id, promo_id, "yoomoney")
    #     else:
    #         await callback.answer("Не оплачено!")


@callbacks_router.callback_query(F.data.startswith("buy_rate"))
async def buy_rate(callback: CallbackQuery):
    rate_id = callback.data.split("_")[-1]
    bot_id = callback.data.split("_")[-2]
    user = db.get_user_by_user_id(callback.from_user.id, bot_id)
    promo_id = user[0][14]
    pay_types = db.get_pay_types(bot_id)
    await callback.message.edit_text(f'Выберите способ оплаты', parse_mode="HTML", disable_web_page_preview=True,
                                  reply_markup=client_markup.create_markup_pay_types(pay_types, rate_id, promo_id=promo_id))


@callbacks_router.callback_query(F.data.startswith("list_of_rates_"))
async def list_of_rates_(callback: CallbackQuery):
    bot_id = callback.data.split("_")[-1]
    rates = db.get_all_rates_by_bot_id(bot_id)
    price_per_minute = db.get_price_per_minute(bot_id)[0][0]
    await callback.message.edit_text(f"Минута моего аудио-ответа стоит {price_per_minute}₽. "
                         f"Твои сообщения на 100% бесплатные.\n\nКакой тариф выберешь?😉",
                         reply_markup=client_markup.create_markup_choice_rate(rates, bot_id))


# @callbacks_router.callback_query(F.data.startswith("yes_promo"))
# async def yes_promo(callback: CallbackQuery, state: FSMContext):
#     rate_id = callback.data.split("_")[-1]
#     bot_id = callback.data.split("_")[-2]
#     await state.set_state(FSM.FSMUser.get_promo)
#     msg = await callback.message.edit_text("Пришлите ваш промокод", reply_markup=client_markup.create_markup_cancel())
#     await state.set_data({"rate_id": rate_id, "bot_id": bot_id, "msg_id": msg.message_id})


@callbacks_router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    # data = await state.get_data()
    # bot_id = data["bot_id"]
    # rates = db.get_all_rates_by_bot_id(bot_id)
    # price_per_minute = db.get_price_per_minute(bot_id)[0][0]
    # await callback.message.edit_text(f"Минута моего аудио-ответа стоит {price_per_minute}₽. "
    #                      f"Твои сообщения на 100% бесплатные.\n\nКакой тариф выберешь?😉",
    #                      reply_markup=client_markup.create_markup_choice_rate(rates, bot_id))
    await state.clear()
    await callback.message.answer("<b>Действие отменено</b>", reply_markup=client_markup.create_start_markup())


@callbacks_router.callback_query(F.data.startswith("cancel"))
async def cancel_pay(callback: CallbackQuery, state: FSMContext):
    rate_id = callback.data.split("_")[-1]
    bot_id, _ = db.get_count_minutes_by_rate(rate_id)[0]
    rates = db.get_all_rates_by_bot_id(bot_id)
    price_per_minute = db.get_price_per_minute(bot_id)[0][0]
    await callback.message.edit_text(f"Минута моего аудио-ответа стоит {price_per_minute}₽. "
                         f"Твои сообщения на 100% бесплатные.\n\nКакой тариф выберешь?😉",
                         reply_markup=client_markup.create_markup_choice_rate(rates, bot_id))
    await state.clear()


@callbacks_router.callback_query(F.data.startswith("pay_"))
async def pay_type_(callback: CallbackQuery):
    rate_id = callback.data.split("_")[-2]
    pay_type_id = callback.data.split("_")[-3]
    promo_id = callback.data.split("_")[-1]
    count_minutes, amount, amount_dollar = db.get_amount_by_rate_id(rate_id)
    discount_percent = None
    if promo_id != "None":
        promo = db.get_promo(int(promo_id))
        discount_percent = int(promo[0][3])
        amount_with_discount = round(amount * (1 - discount_percent / 100), 2)
        amount_with_discount_dollar = round(amount_dollar * (1 - discount_percent / 100), 2)
    else:
        amount_with_discount = amount
        amount_with_discount_dollar = amount_dollar
    discount_percent = "" if discount_percent is None else f"(скидка {discount_percent}%)"
    if pay_type_id == "yoomoney":
        bot_id, _ = db.get_count_minutes_by_rate(int(rate_id))[0]
        yoomoney_token = db.get_yoomoney_token(rate_id)[0][0]
        wallet = Payment(config.yoomoney_wallet, yoomoney_token)
        url, bill = wallet.create_payment(3)
        mark_id = db.get_mark_id_by_user_id(bot_id, callback.from_user.id)
        db.add_payment(bill, callback.from_user.id, bot_id, amount_with_discount, mark_id, promo_id, "yoomoney", rate_id)

#         await callback.message.edit_text(f"""Тариф: <b>{count_minutes} минут - {amount} руб</b>
# Способ оплаты: <b>Yoomoney</b>
# Сумма к оплате: <b>{amount_with_discount}₽ / {amount_with_discount_dollar}$</b> {discount_percent}
# Счет на оплату создан, перейдите по <a href="{url}">ссылке</a> и оплатите тариф. Затем вернитесь сюда и нажмите “Я оплатил(а)”""", parse_mode="HTML", disable_web_page_preview=True,
#                              reply_markup=client_markup.create_markup_payment(url, bill, rate_id, promo_id))
        await callback.message.edit_text(f"""✅ Счет на оплату создан, нажмите 'Перейти к оплате' и оплатите тариф.
Сумма к оплате: <b>{amount_with_discount}₽ / {amount_with_discount_dollar}$</b> {discount_percent}

Внимание!!! После оплаты ожидайте подключения подписки. Если этого не произошло, обратитесь к администрации.""",
                                         parse_mode="HTML", disable_web_page_preview=True,
                                         reply_markup=client_markup.create_markup_payment(url, bill, rate_id, promo_id))

    else:
        pay_type = db.get_pay_type_by_id(pay_type_id)
        await callback.message.edit_text(f"""Тариф: <b>{count_minutes} минут - {amount} руб</b>
Способ оплаты: <b>{pay_type[2]}</b>
Сумма к оплате: <b>{amount_with_discount}₽ / {amount_with_discount_dollar}$</b> {discount_percent}
Информация об оплате:
{pay_type[3]}""",
                                      reply_markup=client_markup.create_markup_payment(url=None, bill_id=None, rate_id=rate_id, promo_id=promo_id, pay_type_id=pay_type[0]))


# @callbacks_router.callback_query(F.data.startswith("no_promo"))
# async def no_promo(callback: CallbackQuery):
#     rate_id = callback.data.split("_")[-1]
#     bot_id = callback.data.split("_")[-2]
#     pay_types = db.get_pay_types(bot_id)
#     await callback.message.edit_text(f'Выберите способ оплаты', parse_mode="HTML", disable_web_page_preview=True,
#                                   reply_markup=client_markup.create_markup_pay_types(pay_types, rate_id, promo_id=None))


@callbacks_router.callback_query(F.data.startswith("accept_"))
async def accept_(callback: CallbackQuery, bot: Bot):
    # pay_type_id = callback.data.split("_")[-1]
    # promo_id = callback.data.split("_")[-2]
    # promo_id = None if promo_id == "None" else promo_id
    rate_id = callback.data.split("_")[-3]
    row_id = callback.data.split("_")[-1]
    user_id = callback.data.split("_")[-2]
    is_check_admin = db.get_payment_by_row_id(row_id)
    if not is_check_admin:
        # pay_type = db.get_pay_type_by_id(pay_type_id)
        bot_id, count_minutes = db.get_count_minutes_by_rate(rate_id)[0]
        # amount = db.get_amount_by_rate_id(rate_id)[1]
        # mark_id = db.get_mark_id_by_user_id(bot_id, user_id)
        db.add_minutes(user_id, bot_id, count_minutes)
        db.update_payment_row(row_id, 1)
        # db.add_payment(None, callback.from_user.id, bot_id, amount, mark_id, promo_id, pay_type[2])
        await bot.send_message(user_id, "Платеж был подтвержден")
        await callback.answer("Платеж был подтвержден")
    else:
        await callback.message.answer("Данный платеж уже был проверен другим администратором")


@callbacks_router.callback_query(F.data.startswith("decline_"))
async def decline_(callback: CallbackQuery, bot: Bot):
    row_id = callback.data.split("_")[-1]
    user_id = callback.data.split("_")[-2]
    is_check_admin = db.get_payment_by_row_id(row_id)
    if not is_check_admin:
        await bot.send_message(user_id, "Платеж не был подтвержден")
        db.update_payment_row(row_id, 0)
    else:
        await callback.message.answer("Данный платеж уже был проверен другим администратором")
