from aiogram import types
import replicas.replicas_main_bot as replicas


def create_start_markup():
    kb = [
        [types.KeyboardButton(text=replicas.create_character)],
        [types.KeyboardButton(text=replicas.my_character)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


def create_markup_start_stop_bot(status, bot_id):
    if status == "запущен":
        kb = [
            [types.InlineKeyboardButton(text="Остановить", callback_data=f"stop_bot_{bot_id}")],
        ]
    else:
        kb = [
            [types.InlineKeyboardButton(text="Запустить", callback_data=f"start_bot_{bot_id}")],
        ]
    kb.append([types.InlineKeyboardButton(text="Изменить промпт", callback_data=f"edit_prompt_{bot_id}")])
    kb.append([types.InlineKeyboardButton(text="Изменить токен yoomoney", callback_data=f"edit_yoomoney_token_{bot_id}")])
    kb.append([types.InlineKeyboardButton(text="Изменить голос", callback_data=f"edit_voice_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Изменить цену за одну минуту", callback_data=f"edit_price_per_minute_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Изменить тарифы", callback_data=f"edit_main_rates_{bot_id}")],)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_cancel_markup():
    kb = [
        [types.KeyboardButton(text=replicas.cancel)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


def create_markup_rates(bot_id):
    kb = [
        [types.InlineKeyboardButton(text="Добавить тариф ➕", callback_data=f"add_rate_{bot_id}")],
        [types.InlineKeyboardButton(text="Удалить тариф ➖", callback_data=f"delete_rates_{bot_id}")],
        [types.InlineKeyboardButton(text="Редактировать тариф", callback_data=f"edit_rates_{bot_id}")],
        [types.InlineKeyboardButton(text="Настроил! Давай дальше ⏩", callback_data=f"next_settings_rate")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_delete_rate(rates):
    kb = []
    for rate in rates:
        kb.append([types.InlineKeyboardButton(text=f"{rate[2]} минут - {rate[3]}₽", callback_data=f"delete_rate_{rate[0]}")])
    kb.append([types.InlineKeyboardButton(text=f"Назад ⏪", callback_data=f"rate_back")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_edit_rate(rates):
    kb = []
    for rate in rates:
        kb.append([types.InlineKeyboardButton(text=f"{rate[2]} минут - {rate[3]}₽", callback_data=f"edit_rate_{rate[0]}")])
    kb.append([types.InlineKeyboardButton(text=f"Назад ⏪", callback_data=f"rate_back")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_rate_back():
    kb = [[types.InlineKeyboardButton(text=f"Назад ⏪", callback_data=f"rate_back")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
