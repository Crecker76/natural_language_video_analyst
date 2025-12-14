from loguru import logger

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


from src.vpn_bot.handlers import handlers_router


storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def start_bot(bot):
    """Функция старта бота"""

    logger.info('Старт бота')
    dp.include_routers(
        handlers_router
    )
    await dp.start_polling(bot)
