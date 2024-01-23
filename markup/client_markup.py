from aiogram import types
import replicas.replicas_sub_bot as replicas


def create_markup_choice_rate(rates, bot_id):
    buttons = []
    if len(rates) > 0:
        start_price_per_minute = int(rates[0][3]) / int(rates[0][2])
        for index, rate in enumerate(rates, 0):
            if index > 0:
                current_price_per_minute = int(rate[3]) / int(rate[2])
                discount = (1 - current_price_per_minute / start_price_per_minute) * 100
                buttons.append([types.InlineKeyboardButton(text=f"{rate[2]} мин - {rate[3]}₽ / {rate[4]}$ (скидка {round(discount)}%)",
                                                       callback_data=f"buy_rate_{bot_id}_{rate[0]}")])
            else:
                buttons.append([types.InlineKeyboardButton(text=f"{rate[2]} мин - {rate[3]}₽ / {rate[4]}$",
                                                       callback_data=f"buy_rate_{bot_id}_{rate[0]}")])
    else:
        for index, rate in enumerate(rates, 0):

            buttons.append([types.InlineKeyboardButton(text=f"{rate[2]} мин - {rate[3]}₽", callback_data=f"buy_rate_{bot_id}_{rate[0]}")])
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


def create_markup_subscribe(bot_id):
    buttons = [[types.InlineKeyboardButton(text=f"🛒 Список тарифов", callback_data=f"list_of_rates_{bot_id}")]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


def create_markup_payment(url, bill_id, rate_id, promo_id, pay_type_id=None):
    if url is None:
        buttons = [[types.InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data=f"payment_{promo_id}_{rate_id}_{pay_type_id}")],
                   [types.InlineKeyboardButton(text="✖ Отменить", callback_data=f"cancel_{rate_id}")]]
    else:
        # buttons = [
        #     [types.InlineKeyboardButton(text="Оплатить", url=url)],
        #     [types.InlineKeyboardButton(text="✅ Я оплатил(а)", callback_data=f"payment_{promo_id}_{rate_id}_{bill_id}")],
        #     [types.InlineKeyboardButton(text="✖ Отменить", callback_data=f"cancel_{rate_id}")]
        #
        # ]
        buttons = [[types.InlineKeyboardButton(text="✅ Перейти к оплате", url=url)]]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


# def create_markup_promocode(rate_id, bot_id):
#     buttons = [
#         [types.InlineKeyboardButton(text="Да, есть", callback_data=f"yes_promo_{bot_id}_{rate_id}")],
#         [types.InlineKeyboardButton(text="Нет", callback_data=f"no_promo_{bot_id}_{rate_id}")]
#
#     ]
#     markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
#     return markup


def create_markup_cancel():
    buttons = [
        [types.InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel")],
    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup


def create_markup_pay_types(pay_types, rate_id, promo_id):
    kb = []
    for pay_type in pay_types:
        if pay_type[4]:
            kb.append([types.InlineKeyboardButton(text=pay_type[2], callback_data=f"pay_{pay_type[0]}_{rate_id}_{promo_id}")])
    kb.append([types.InlineKeyboardButton(text="ЮМани", callback_data=f"pay_yoomoney_{rate_id}_{promo_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_accept_pay(user_id, row_id, rate_id):
    buttons = [
        [types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"accept_{rate_id}_{user_id}_{row_id}")],
        [types.InlineKeyboardButton(text="✖ Спам", callback_data=f"decline_{user_id}_{row_id}")]

    ]
    markup = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return markup

def create_start_markup():
    buttons = [
        [types.KeyboardButton(text=replicas.rates), types.KeyboardButton(text=replicas.subscribe)],
        [types.KeyboardButton(text=replicas.feedback)],

    ]
    markup = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    return markup

