from aiogram import Router, types
from aiogram.filters import Command

from loguru import logger

from src.api_open_ai.generating_requests_to_AI import generate_sql
from src.vpn_bot.utils_bot import get_answer

router = Router()


# Опционально: приветствие по /start
@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! 👋\n"
        "Я бот-аналитик видео.\n"
        "Задавай вопросы на русском про статистику — отвечу только числом.\n\n"
        "Примеры:\n"
        "• Сколько всего видео есть в системе?\n"
    )


# Главный — ловим любой текст
@router.message()
async def analytics_handler(message: types.Message):

    question = message.text.strip()
    if not question:
        return

    # Показываем индикатор
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        # Делаем запрос на формирование SQL запроса от AI
        answer = await get_answer(question=question)
        # Отправляем готовый ответ пользователю
        await message.answer(str(answer))
    except Exception as e:
        logger.error(f"Ошибка при обработке вопроса: {e}")
        await message.answer("Ошибка, попробуй позже")