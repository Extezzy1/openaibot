from aiogram.fsm.state import StatesGroup, State


class FSMAdmin(StatesGroup):
    get_prompt = State()
    get_token_bot = State()
    get_voice = State()
    get_rates = State()
    get_yoomoney_token = State()
    get_price_per_minute = State()

    get_start_text = State()
    get_start_photo = State()

    # Редактирование параметров в настройках
    get_new_yoomoney_token = State()
    get_new_prompt = State()
    get_new_voice = State()
    get_new_price_per_minute = State()
    get_new_start_text = State()
    get_new_start_photo = State()

    # Добавление тарифа
    get_count_minutes = State()
    get_price = State()
    get_price_dollar = State()

    # Добавление промокода
    get_title_promo = State()
    get_discount_percent = State()
    get_count_activation_total = State()
    get_count_activation_by_person = State()
    get_date_end = State()

    # Редактирование тарифа
    get_new_count_minutes = State()
    get_new_price = State()
    get_new_dollar_price = State()

    # Добавление метки
    get_mark_name = State()

    # Редактирование промокода
    get_new_count_activation_total = State()
    get_new_count_activation_by_person = State()
    get_new_date_end = State()

    # Рассылка
    get_text = State()
    get_photo = State()

    # Способы оплаты
    get_title_pay_type = State()
    get_description_pay_type = State()

    # Редактирование способа оплаты
    get_new_title_pay_type = State()
    get_new_description_pay_type = State()

    # Фидбек
    get_text_answer_user = State()

class FSMUser(StatesGroup):
    get_text_feedback = State()
    get_promo = State()
    get_photo_document_pay = State()