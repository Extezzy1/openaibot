from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import FSM
from polling_manager import add_bot, stop_bot
from dispatchers import dp_new_bot, polling_manager
from db_ import db
import markup.admin_markup as admin_markup


callbacks_router = Router()


@callbacks_router.callback_query(F.data == "next_settings_rate")
async def next_settings_rate(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    rates = db.get_all_rates_by_bot_id(data["token"].split(":")[0])
    if len(rates) > 0:
        await state.clear()
        await callback.message.answer("Главное меню", reply_markup=admin_markup.create_start_markup())
    else:

        await callback.message.answer("Добавь хотя бы один тариф, чтобы закончить настройку")


@callbacks_router.callback_query(F.data.startswith("edit_main_rates"))
async def edit_rates(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSM.FSMAdmin.get_rates)
    bot_id = callback.data.split("_")[-1]
    token = db.get_bot_token(bot_id)
    await state.set_data({"token": token})
    rates = db.get_all_rates_by_bot_id(bot_id)
    current_rates = ""
    for rate in rates:
        current_rates += f"{rate[2]} минут - {rate[3]}₽\n"
    await callback.message.answer(f"Текущие тарифы:\n{current_rates}",
                         reply_markup=admin_markup.create_markup_rates(bot_id))


@callbacks_router.callback_query(F.data.startswith("edit_rates"))
async def edit_rates(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_id = data["token"].split(":")[0]
    rates = db.get_all_rates_by_bot_id(bot_id)
    await callback.message.edit_text("Выбери тариф для изменения", reply_markup=admin_markup.create_markup_edit_rate(rates))


@callbacks_router.callback_query(F.data.startswith("edit_rate"))
async def edit_rate(callback: CallbackQuery, state: FSMContext):
    rate_id = callback.data.split("_")[-1]
    await callback.message.delete()
    data = await state.get_data()
    msg = await callback.message.answer("Введи новое время в минутах тарифа (целое число)")
    data["edit_rate_id"] = rate_id
    data["msg_id"] = msg.message_id

    await state.set_data(data)
    await state.set_state(FSM.FSMAdmin.get_new_count_minutes)


@callbacks_router.callback_query(F.data.startswith("add_rate"))
async def add_rate(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSM.FSMAdmin.get_count_minutes)
    await callback.message.delete()
    msg = await callback.message.answer("Введи время в минутах тарифа (целое число)", reply_markup=admin_markup.create_markup_rate_back())
    data = await state.get_data()
    data["msg_id"] = msg.message_id
    await state.set_data(data)


@callbacks_router.callback_query(F.data.startswith("delete_rates"))
async def delete_rates(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_id = data["token"].split(":")[0]
    rates = db.get_all_rates_by_bot_id(bot_id)
    await callback.message.edit_text("Выбери тариф для удаления", reply_markup=admin_markup.create_markup_delete_rate(rates))


@callbacks_router.callback_query(F.data == "rate_back")
async def rate_back(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    bot_id = data["token"].split(":")[0]
    rates = db.get_all_rates_by_bot_id(bot_id)
    current_rates = ""
    for rate in rates:
        current_rates += f"{rate[2]} минут - {rate[3]}₽\n"
    await callback.message.delete()
    await callback.message.answer(f"Текущие тарифы:\n{current_rates}",
                         reply_markup=admin_markup.create_markup_rates(bot_id))


@callbacks_router.callback_query(F.data.startswith("delete_rate_"))
async def delete_rate(callback: CallbackQuery, state: FSMContext):
    rate_id = callback.data.split("_")[-1]
    db.delete_rate(rate_id)
    data = await state.get_data()
    bot_id = data["token"].split(":")[0]
    rates = db.get_all_rates_by_bot_id(bot_id)
    current_rates = ""
    for rate in rates:
        current_rates += f"{rate[2]} минут - {rate[3]}₽\n"
    await callback.message.edit_text(f"Успешно удалил тариф!\n\nТекущие тарифы:\n{current_rates}",
                         reply_markup=admin_markup.create_markup_rates(bot_id))


@callbacks_router.callback_query(F.data.startswith("start_bot"))
async def start_bot_callback(callback: CallbackQuery):
    bot_id = callback.data.split("_")[-1]
    bot_token = db.get_bot_token(bot_id)
    _, _, bot_id = await add_bot(bot_token, dp_new_bot, polling_manager)
    if bot_id:
        db.update_status_bot(bot_token, "запущен")
        # await callback.message.answer("Персонаж успешно запущен!", reply_markup=admin_markup.create_start_markup())
        await callback.message.edit_text(text=f'<i>Персонаж успешно запущен!</i>\n\n{callback.message.text[callback.message.text.index("["):].replace("остановлен", "запущен").replace("не запущен", "запущен")}', reply_markup=admin_markup.create_markup_start_stop_bot('запущен', bot_id), parse_mode='HTML')
    else:
        await callback.message.answer("Не удалось запустить персонажа", reply_markup=admin_markup.create_start_markup())


@callbacks_router.callback_query(F.data.startswith("stop_bot"))
async def stop_bot_callback(callback: CallbackQuery):
    bot_id = int(callback.data.split("_")[-1])
    bot_token = db.get_bot_token(bot_id)
    if await stop_bot(bot_id, polling_manager):
        db.update_status_bot(bot_token, "остановлен")
        # await callback.message.answer("Персонаж остановлен", reply_markup=admin_markup.create_start_markup())
        await callback.message.edit_text(text=f'<i>Персонаж остановлен</i>\n\n{callback.message.text[callback.message.text.index("["):].replace("запущен", "остановлен")}', reply_markup=admin_markup.create_markup_start_stop_bot('остановлен', bot_id), parse_mode='HTML')
    else:
        await callback.message.answer("Не удалось остановить персонажа", reply_markup=admin_markup.create_start_markup())


@callbacks_router.callback_query(F.data.startswith("edit_prompt_"))
async def edit_prompt_(callback: CallbackQuery, state: FSMContext):
    bot_id = int(callback.data.split("_")[-1])
    await callback.message.delete()
    await callback.message.answer("Пришли мне новый промпт", reply_markup=admin_markup.create_cancel_markup())
    await state.set_state(FSM.FSMAdmin.get_new_prompt)
    await state.set_data({"bot_id": bot_id})


@callbacks_router.callback_query(F.data.startswith("edit_yoomoney_token_"))
async def edit_yoomoney_token(callback: CallbackQuery, state: FSMContext):
    bot_id = int(callback.data.split("_")[-1])
    await callback.message.delete()
    await callback.message.answer("Пришли мне новый токен yoomoney", reply_markup=admin_markup.create_cancel_markup())
    await state.set_state(FSM.FSMAdmin.get_new_yoomoney_token)
    await state.set_data({"bot_id": bot_id})


@callbacks_router.callback_query(F.data.startswith("edit_voice_"))
async def edit_voice_(callback: CallbackQuery, state: FSMContext):
    bot_id = int(callback.data.split("_")[-1])
    await callback.message.delete()
    await callback.message.answer("Пришли мне новый голос персонажа", reply_markup=admin_markup.create_cancel_markup())
    await state.set_state(FSM.FSMAdmin.get_new_voice)
    await state.set_data({"bot_id": bot_id})



@callbacks_router.callback_query(F.data.startswith("edit_price_per_minute_"))
async def edit_price_per_minute_(callback: CallbackQuery, state: FSMContext):
    bot_id = int(callback.data.split("_")[-1])
    await callback.message.delete()
    await callback.message.answer("Пришли мне новую цену за минуту персонажа", reply_markup=admin_markup.create_cancel_markup())
    await state.set_state(FSM.FSMAdmin.get_new_price_per_minute)
    await state.set_data({"bot_id": bot_id})
