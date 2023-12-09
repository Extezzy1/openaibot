import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.sub_bot.commands import commands_router
# from handlers.callbacks import callbacks_router
import config


async def main() -> None:
    bot = Bot(token=config.token_bot, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    # dp.include_routers(callbacks_router, commands_router)
    dp.include_routers(commands_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())