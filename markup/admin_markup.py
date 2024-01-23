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
    kb.append([types.InlineKeyboardButton(text="Изменить стартовое сообщение", callback_data=f"edit_start_message_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Настроить тарифы", callback_data=f"edit_main_rates_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Настроить метки", callback_data=f"edit_marks_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Промокоды", callback_data=f"promocodes_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Рассылка", callback_data=f"mailing_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Статистика", callback_data=f"statistics_{bot_id}")],)
    kb.append([types.InlineKeyboardButton(text="Способы оплаты", callback_data=f"manual_pay_{bot_id}")],)
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


def create_markup_edit_start_photo():
    kb = [[types.InlineKeyboardButton(text=f"Да, добавляем!", callback_data=f"edit_photo")],
          [types.InlineKeyboardButton(text=f"Нет, идем дальше ⏩ / Сбросить текущее фото", callback_data=f"skip_edit_photo")]]
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


def create_markup_promocodes(promocodes, bot_id):
    kb = []
    for promocode in promocodes:
        kb.append([types.InlineKeyboardButton(text=promocode[2], callback_data=f"promocode_{bot_id}_{promocode[0]}")])
    kb.append([types.InlineKeyboardButton(text="➕ Создать промокод", callback_data=f"add_promocode_{bot_id}")])
    kb.append([types.InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"back_to_settings_{bot_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_promocode(bot_id, promo_id):
    kb = [
        [types.InlineKeyboardButton(text="✏️ Изменить кол-во активаций", callback_data=f"edit_promo_total_{promo_id}_{bot_id}")],
        [types.InlineKeyboardButton(text=f"✏️ Изменить кол-во активаций на человека", callback_data=f"edit_promo_person_{promo_id}_{bot_id}")],
        [types.InlineKeyboardButton(text=f"✏️ Изменить срок действия промокода", callback_data=f"edit_promo_date_{promo_id}_{bot_id}")],
        [types.InlineKeyboardButton(text=f"Список активаций", callback_data=f"promo_statistics_{promo_id}")],
        [types.InlineKeyboardButton(text=f"🗑️ Удалить", callback_data=f"delete_promo_{promo_id}_{bot_id}")],
        [types.InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"back_to_promocodes_{bot_id}")]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_mailing():
    kb = [
        [types.KeyboardButton(text=replicas.show_message)],
        [types.KeyboardButton(text=replicas.cancel_mailing), types.KeyboardButton(text=replicas.send)]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


# def create_markup_mailing_photo():
#     kb = [
#         [types.KeyboardButton(text=replicas.end_add_photo)],
#     ]
#     keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
#     return keyboard


def create_markup_mailing_type():
    kb = [
        [types.KeyboardButton(text=replicas.mailing_all)],
        [types.KeyboardButton(text=replicas.mailing_without_subscribe)],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard


def create_markup_manual_pay(bot_id, pay_types):
    kb = []
    for pay_type in pay_types:
        kb.append([types.InlineKeyboardButton(text=pay_type[2], callback_data=f"manual_type_{pay_type[0]}")])
    kb.append([types.InlineKeyboardButton(text="➕ Создать новый способ оплаты", callback_data=f"add_manual_type_{bot_id}")])
    kb.append([types.InlineKeyboardButton(text="Статистика", callback_data=f"statistics_manual_type_{bot_id}")])
    kb.append([types.InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"back_to_settings_{bot_id}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_edit_manual_pay_type(pay_type_id, bot_id, is_enable):
    kb = [
        [types.InlineKeyboardButton(text="✏️ Название", callback_data=f"change_name_pay_type_{pay_type_id}"),
         types.InlineKeyboardButton(text=f"✏️ Описание", callback_data=f"change_description_pay_type_{pay_type_id}")],
        [types.InlineKeyboardButton(text="Отключить" if is_enable == 1 else "Включить", callback_data=f"disable_pay_type_{pay_type_id}"),
         types.InlineKeyboardButton(text=f"🗑️ Удалить", callback_data=f"delete_pay_{bot_id}_{pay_type_id}")],
        [types.InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"back_to_manual_pay_{bot_id}")]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard


def create_markup_feedback(message_id, user_id, bot_id):
    kb = [
        [types.InlineKeyboardButton(text="✉️ Ответить", callback_data=f"answer_feedback_{message_id}")],
         [types.InlineKeyboardButton(text=f"🔨 Забанить пользователя", callback_data=f"ban_{user_id}_{bot_id}")]
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    return keyboard
