import re
from asyncio import sleep
import os
from datetime import datetime, timedelta
from io import BytesIO

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, Message, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext


from src.database.method_db import create_object, update_attribute_object, get_by_attribute
from src.database.models import User, Devices
from src.vpn_service import ThreeXRayClientManager

from loguru import logger


def generate_unique_email(user: User, user_list: list):
    """
    Проверка на уникальности имени в инбаунде
    :param user: объект пользователя
    :param user_list: список пользователей в инбаунде

    :return name_file : str
    """
    base_email = f"{user.telegram_id}_user"

    # собираем все существующие email для этого пользователя
    existing = [u['email'] for u in user_list if u['email'].startswith(base_email)]

    if not existing:
        return base_email  # если ещё нет — создаём базовый

    # ищем максимальный суффикс "_N"
    max_suffix = 0
    for email in existing:
        match = re.match(rf"^{base_email}_(\d+)$", email)
        if match:
            suffix = int(match.group(1))
            max_suffix = max(max_suffix, suffix)

    return f"{base_email}_{max_suffix + 1}"


def create_inline_keyboard(list_but: list[InlineKeyboardButton]):
    """Функция расположения кнопок по столбцам"""

    number_columns_for_buttons = 1  # Количество столбцов для расположения кнопок
    builder = InlineKeyboardBuilder()
    for i in range(0, len(list_but), number_columns_for_buttons):
        builder.row(*list_but[i:i + number_columns_for_buttons])
    return builder.as_markup()


async def wait_for_timeout(message: Message, state: FSMContext):
    """Функция таймера ответа для пользователей, для сброса ожидания ответа"""
    await sleep(10)  # Задержка в 5 минут
    await state.set_state()  # Сбрасываем состояние, если пользователь не ответил
    await message.answer('Время ожидания ответа истекло')


def call_user_bot_end_sub():
    """Оповещение пользователя"""
    pass


# Функция для удаления файла
def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)  # Удаляем файл
            print(f"Файл {file_path} успешно удален.")
            return True
        else:
            print(f"Файл {file_path} не существует.")
            return False
    except Exception as e:
        print(f"Ошибка при удалении файла {file_path}: {e}")


def get_user_info_and_device_info(user: User):
    """Получение информации о пользователе и его устройствах"""

    tab = '   '
    info_from_devices = '\n'.join([
        f'ℹ️{tab}{device.type_device} - {device.name}\n'
        f'{tab}Начало: {device.date_start_subscription.strftime("%H:%M  %d.%m.%Y")}\n'
        f'{tab}Конец: {device.date_end_subscription.strftime("%H:%M  %d.%m.%Y")}\n'
        '---------------' for device in user.devices
    ])
    return (
        f'Имя: {user.name}\n'
        f'Id in Tel: {user.telegram_id}\n'
        f'Дата регистрации: {user.date_registration.strftime("%H:%M  %d.%m.%Y")}\n\n'
        f'Количество устройств- {len(user.devices)}:\n'
        f'{info_from_devices}'
    )


def create_file(data_list: list[str], name_document: str) -> BufferedInputFile | None:
    """
    Создает файл в формате BytesIO из списка данных.

    :param data_list: Список строк, которые будут записаны в файл.
    :param name_document: Имя документа
    :return: Объект InputFile с записанными данными.
    """

    byte_io = BytesIO()
    for line in data_list:
        byte_io.write((line + '\n').encode('utf-8'))

    byte_io.seek(0)
    file_content = byte_io.read()

    if not file_content:
        # Если файл пустой или не удалось создать, возвращаем None
        return None
    return BufferedInputFile(file_content, filename=name_document)


async def create_new_device_and_config(user: User, type_os: str, duration_days: int = 30) -> Devices | bool:
    """
    Создание конфигурация нового устройства и создание записи в БД

    :param user - модель пользователя в БД
    :param type_os - тип операционной системы устройства
    :param duration_days - длина подписки в днях, для сохранения данных в БД

    :return объект девайся
    """
    try:
        # Получили нужный сервер + инбаунд внутри
        obj_server, manager_current_server = ThreeXRayClientManager.get_client_for_available_server()

        # Получаем всех клиентов на сервере , чтобы сделать имя настроек уникальным
        user_list = []
        for protocol in obj_server.protocols:
            user_list.extend(manager_current_server.get_users_inbound(
                inbound_id=protocol.external_id
            ))
        logger.info(f'Список пользователей сервера: {user_list}')
        # Генерируем уникальное имя конфигов
        name_config = generate_unique_email(
            user=user,
            user_list=user_list
        )
        # создаем нового клиента на сервере
        client_id_from_server = manager_current_server.add_client(
            email=name_config,
            inbound_id=manager_current_server.protocol.external_id
        )
        # Получаем ссылку с настройками
        config_link = manager_current_server.get_client_config(
            inbound_id=manager_current_server.protocol.external_id,
            client_id=client_id_from_server,
            client_telegram_id=f'{user.telegram_id}_user'
        )

        # Создание нового объекта устройства в БД
        new_device = create_object(
            user=user,
            model=Devices,
            payment=True,
            type_device=type_os,
            date_end_subscription=datetime.now()+timedelta(days=duration_days),
            data_connect={
                "inbound_id": manager_current_server.protocol.external_id,
                "config_link": config_link,
                "user_id_in_protocol": client_id_from_server
            },
            server=obj_server
        )
        if new_device:
            # Добавление нового устройства в список пользователя
            user.devices.append(new_device)
            # убираем бесплатный план
            user.free_plan = False
            # Обновление атрибутов
            update_attribute_object(obj=user)
        logger.info(
            'Конфигурация создана - с бесплатным периодом\n'
            f'Пользователь: {user.name}\n'
            f'Тип устройства: {type_os}\n'
            f'ID-устройства: {new_device.device_id}\n'
        )
        return new_device
    except Exception:
        logger.exception('Ошибка при создании конфигурации и нового объекта в БД')
        return False


async def handle_referral(user: User, ref_code: str, bot: Bot) -> None:
    """
    Обработка реферальных ссылок пользователей

    :param user - объект приглашенного пользователя
    :param ref_code - код пригласившего пользователя == ref_(telegram_id)
    :param bot - объект бота для отправки сообщений

    :return None
    """

    try:
        # достаем id пригласившего
        ref_data = ref_code.replace("ref_", "")
        if isinstance(ref_data, int):
            raise ValueError
        referrer_telegram_id = int(ref_data)

        # Защита от самоприглашения
        if referrer_telegram_id == user.telegram_id:
            await bot.send_message(
                user.telegram_id,
                text="Вы не можете пригласить самого себя"
            )
            return

        # Достаем кто пригласил
        referrer = get_by_attribute(
            model=User,
            attr_name="telegram_id",
            attr_value=referrer_telegram_id
        )

        # Неизвестный пригласивший
        if not referrer:
            logger.error(f"Пользователь- РЕФЕРАЛ с телеграмм id {referrer_telegram_id} не нашелся в БД")
            return

        # Уже есть реферер — не меняем
        if user.referred_by:
            await bot.send_message(
                user.telegram_id,
                text=f"Вы уже приглашены пользователем {user.referred_by}"
            )
            return

        # Привязка
        user.referred_by = referrer.user_id
        update_attribute_object(user)  # или session.commit(), если работаешь с сессией напрямую

        # Уведомляем пригласившего
        try:
            await bot.send_message(
                chat_id=referrer_telegram_id,
                text=f"🎉 По вашей ссылке зарегистрировался пользователь: @{user.name}\n",
                reply_markup=create_inline_keyboard(
                    list_but=[
                        InlineKeyboardButton(
                            text="Как пользоваться бесплатно",
                            callback_data="referral_system"
                        )
                    ]
                )
            )
        except Exception:
            logger.exception("Ошибка при отправке уведомления пригласившему")

    except Exception as e:
        logger.exception(f"Ошибка в обработке реферального кода: {e}")
