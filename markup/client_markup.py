from aiogram import types


def create_markup_choice_rate(rates):
    buttons = []
    for rate in rates:
        buttons.append([types.InlineKeyboardButton(text=f"{rate[2]} мин - {rate[3]}₽", callback_data=f"buy_rate_{rate[0]}")])
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


def create_markup_payment(url, bill_id, rate_id):
    buttons = [
        [types.InlineKeyboardButton(text="Оплатить", url=url)],
        [types.InlineKeyboardButton(text="Я оплатил(а)", callback_data=f"payment_{rate_id}_{bill_id}")]

    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup