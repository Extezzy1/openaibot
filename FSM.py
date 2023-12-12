from aiogram.fsm.state import StatesGroup, State


class FSMAdmin(StatesGroup):
    get_prompt = State()
    get_token_bot = State()
    get_voice = State()
    get_rates = State()
    get_yoomoney_token = State()
    get_price_per_minute = State()

    # Редактирование параметров в настройках
    get_new_yoomoney_token = State()
    get_new_prompt = State()
    get_new_voice = State()
    get_new_price_per_minute = State()


    # Добавление тарифа
    get_count_minutes = State()
    get_price = State()

    # Редактирование тарифа
    get_new_count_minutes = State()
    get_new_price = State()


class FSMUser():
    pass