import asyncio
import logging
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiogram.utils.markdown import html_decoration as fmt
from aiogram.utils.token import TokenValidationError
from aiogram.fsm.storage.memory import MemoryStorage
from dispatchers import dp_new_bot, polling_manager
import config
from polling_manager import PollingManager
from handlers.main_bot.commands import commands_router
from handlers.main_bot.callbacks import callbacks_router

logger = logging.getLogger(__name__)


TOKENS = [
    config.token_bot,
]
dp = Dispatcher(events_isolation=SimpleEventIsolation(), storage=MemoryStorage())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    bots = [Bot(token) for token in TOKENS]
    # dp.startup.register(on_startup)
    # dp.shutdown.register(on_shutdown)
    #
    # dp.message.register(add_bot, Command(commands="add_bot"))
    # dp.message.register(stop_bot, Command(commands="stop_bot"))
    dp.include_routers(commands_router, callbacks_router)
    for bot in bots:
        await bot.get_updates(offset=-1)
    await dp.start_polling(*bots, dp_for_new_bot=dp_new_bot, polling_manager=polling_manager)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Exit")