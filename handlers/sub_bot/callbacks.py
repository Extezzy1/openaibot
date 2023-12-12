from aiogram import Router, F
from aiogram.types import CallbackQuery

import config
from payment import Payment
import markup.client_markup as client_markup
from db_ import db

callbacks_router = Router()


@callbacks_router.callback_query(F.data.startswith("payment_"))
async def payment_successful(callback: CallbackQuery):
    bill_id = callback.data.split("_")[-1]
    rate_id = callback.data.split("_")[-2]
    yoomoney_token = db.get_yoomoney_token(rate_id)[0][0]
    wallet = Payment(config.yoomoney_wallet, yoomoney_token)
    status, amount = wallet.check_payment(bill_id)
    if status == 'Оплачено':
        await callback.message.answer("Успешно оплачено!")
        bot_id, count_minutes = db.get_count_minutes_by_rate(rate_id)[0]
        db.add_minutes(callback.from_user.id, bot_id, count_minutes)
        db.add_payment(bill_id, callback.from_user.id, amount)
    else:
        await callback.answer("Не оплачено!")


@callbacks_router.callback_query(F.data.startswith("buy_rate"))
async def buy_rate(callback: CallbackQuery):
    rate_id = callback.data.split("_")[-1]
    yoomoney_token = db.get_yoomoney_token(rate_id)[0][0]
    wallet = Payment(config.yoomoney_wallet, yoomoney_token)
    url, bill = wallet.create_payment(3)
    await callback.message.answer(f'<a href="{url}">Оплатить</a>', parse_mode="HTML", disable_web_page_preview=True,
                                  reply_markup=client_markup.create_markup_payment(url, bill, rate_id))

