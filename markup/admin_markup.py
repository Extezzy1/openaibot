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
    kb.append([types.InlineKeyboardButton(text="Настроить тарифы", callback_data=f"edit_main_rates_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Настроить метки", callback_data=f"edit_marks_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Статистика", callback_data=f"statistics_{bot_id}")],)
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


def create_markup_add_start_photo():
    kb = [[types.InlineKeyboardButton(text=f"Да, добавляем!", callback_data=f"add_photo")],
          [types.InlineKeyboardButton(text=f"Нет, идем дальше ⏩", callback_data=f"skip_add_photo")]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_choice_marks(bot_id, marks):
    kb = []
    for mark in marks:
        kb.append([types.InlineKeyboardButton(text=mark[2], callback_data=f"mark_{mark[0]}_{bot_id}")])
    kb.append([types.InlineKeyboardButton(text=f"Таблица меток", callback_data=f"table_marks_{bot_id}")])
    kb.append([types.InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"back_to_settings_{bot_id}"),
               types.InlineKeyboardButton(text=f"➕ Создать метку", callback_data=f"create_mark_{bot_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_mark(mark_id, bot_id):
    kb = [[types.InlineKeyboardButton(text=f"Таблица пользователей", callback_data=f"table_users_mark_{mark_id}")],
          [types.InlineKeyboardButton(text=f"🗑️ Удалить", callback_data=f"delete_mark_{mark_id}_{bot_id}")],
          [types.InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"back_to_mark_settings_{bot_id}")]
          ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
