from aiogram import types



def create_markup_payment(url, bill_id):
    buttons = [
        [types.InlineKeyboardButton(text="Оплатить", url=url)],
        [types.InlineKeyboardButton(text="Я оплатил(а)", callback_data=f"payment_successful_{bill_id}")]

    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup