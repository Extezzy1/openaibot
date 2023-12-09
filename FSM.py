from aiogram.fsm.state import StatesGroup, State


class FSMAdmin(StatesGroup):
    get_prompt = State()
    get_token_bot = State()
    get_voice = State()
    get_yoomoney_token = State()
    get_new_yoomoney_token = State()
    get_new_prompt = State()
    get_new_voice = State()


class FSMUser():
    pass