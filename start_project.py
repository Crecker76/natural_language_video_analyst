from datetime import datetime
from asyncio import run, gather


from aiogram import Bot

from config_project.constants import BOT_TOKEN, ENVIRONMENT
from config_project.config import ConfigProject

from src.vpn_bot.bot import start_bot

from loguru import logger


bot = Bot(token=BOT_TOKEN)  # Объект бота
manager_config_project = ConfigProject()  # Объект класса ConfigProject (для предварительной проверки системы)


async def start_project():
    """
    Функция запуска всего проекта в 2 потоках
    """

    try:
        # Запускаем бота
        await start_bot(bot=bot)
    except Exception as e:
        logger.error(f'Ошибка запуска проекта {e}')


if __name__ == '__main__':
    try:
        print(f'Старт проекта в режиме - {ENVIRONMENT} - {datetime.now()}\n')
        if not manager_config_project.prepare_check_project():
            logger.error('Ошибка предварительной проверки системы')
            exit(1)
        logger.info('Проверка проекта прошла успешно')
        # # Запуск проекта
        # run(start_project())
    except KeyboardInterrupt:
        logger.error('Остановка программы с клавиатуры')
        logger.info("Program stopped by user. Shutting down gracefully.\n\n")
    except Exception:
        logger.exception('Ошибка при старте')
