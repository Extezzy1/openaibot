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
    kb.append([types.InlineKeyboardButton(text="Изменить голос", callback_data=f"edit_voice_{bot_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_cancel_markup():
    kb = [
        [types.KeyboardButton(text=replicas.cancel)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard
