from aiogram import Router, F
from aiogram.types import CallbackQuery

from payment import wallet

callbacks_router = Router()


@callbacks_router.callback_query(F.data.startswith("payment_successful"))
async def payment_successful(callback: CallbackQuery):
    bill_id = callback.data.split("_")[-1]
    if wallet.check_payment(bill_id) == 'Оплачено':
        await callback.message.answer("Успешно оплачено!")
    else:
        await callback.answer("Не оплачено!")