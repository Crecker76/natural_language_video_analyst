from loguru import logger

from aiogram import Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage


from src.vpn_bot.handlers import user_router, admin_router


storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()


async def start_bot(bot):
    """Функция старта бота"""

    logger.info('Старт бота')
    dp.include_routers(
        user_router,
        admin_router
    )
    await dp.start_polling(bot)
