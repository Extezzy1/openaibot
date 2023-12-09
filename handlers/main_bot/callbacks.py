from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

import FSM
from polling_manager import add_bot, stop_bot
from dispatchers import dp_new_bot, polling_manager
from db_ import db
import markup.admin_markup as admin_markup


callbacks_router = Router()


@callbacks_router.callback_query(F.data.startswith("start_bot"))
async def start_bot_callback(callback: CallbackQuery):
    bot_id = callback.data.split("_")[-1]
    bot_token = db.get_bot_token(bot_id)
    _, _, bot_id = await add_bot(bot_token, dp_new_bot, polling_manager)
    print(_)
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
