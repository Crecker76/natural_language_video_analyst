from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton

from config_project.constants import NAME_BOT
from src.database.db_selectors import get_rewarded_user_ids
from src.database.method_db import get_by_attribute, create_object, update_attribute_object
from src.database.models import User, Devices, ReferralBonus
from src.vpn_bot.utils_bot import create_inline_keyboard
from src.vpn_service import Xray_api_client

router = Router()


@router.callback_query(F.data == "extend_subscription_for_fifteen_days")
async def extend_subscription_for_month(callback: CallbackQuery):
    """Продление подписки устройства по реферальной системе"""

    await callback.message.chat.delete_message(
        message_id=callback.message.message_id
    )
    # Получаем пользователя по telegram_id
    current_user = get_by_attribute(
        model=User,
        attr_name='telegram_id',
        attr_value=callback.message.chat.id
    )
    if current_user is None or not current_user.devices:
        await callback.message.answer(
            text="У вас нет устройств для продления подписки.Создайте устройство",
            reply_markup=create_inline_keyboard(
                list_but=[
                    InlineKeyboardButton(
                        text="Подключить устройства",
                        callback_data="allocation"
                    )
                ]
            )
        )
        return

    # Создаём inline-кнопки для каждого устройства
    device_buttons = [
        InlineKeyboardButton(
            text=f"{device.name if device.name != 'unknown' else 'Устройство'} ({device.type_device})",
            callback_data=f"extend_device_{device.device_id}"
        )
        for device in current_user.devices
    ]
    # Добавляем кнопку назад
    device_buttons.append(
        InlineKeyboardButton(
            text="⏪ Назад",
            callback_data="referral_system"
        )
    )

    await callback.message.answer(
        text="Выберите устройство для продления подписки:",
        reply_markup=create_inline_keyboard(list_but=device_buttons)
    )


@router.callback_query(F.data == "referral_system")
async def info_from_referral_system(callback: CallbackQuery):
    """Получение доступа к Реферальной системе"""

    await callback.message.chat.delete_message(
        message_id=callback.message.message_id
    )
    # Достаем пользователя
    user = get_by_attribute(
        User,
        attr_name="telegram_id",
        attr_value=callback.from_user.id
    )
    # Достаем только пользователей за которые бонус еще не был получен
    not_rewarded = get_rewarded_user_ids(
        referrer_user_id=user.user_id,
        invited_users=user.referrals
    )
    # Список приглашенных
    list_ref_user: str = ''
    # Массив для отслеживания, что все пользователи оплатили подписку
    payment_status_user = None

    for invited_user in not_rewarded:
        # TODO упростить цикл
        # Достаем платежи приглашенного пользователя
        payments_user = get_by_attribute(
            model=User,
            attr_name="user_id",
            attr_value=invited_user.user_id,
        ).payments

        # Проверяем, что payments загружены и не None
        if payments_user is None or payments_user == []:
            has_success_payment = False
        else:
            has_success_payment = any(payment.status == 'success' for payment in payments_user)
            if has_success_payment:
                payment_status_user = True
        list_ref_user += (
            f'    ▫️ {invited_user.name if invited_user.name != "unknown" else f"unknown - {invited_user.telegram_id}"}'
            f'{" ✅ - можно получить продление подписки" if has_success_payment else " ❌ подписка не куплена"}\n'
        )

    ref_link = f"https://t.me/{NAME_BOT}?start=ref_{user.telegram_id}"
    text = (
        f"🎁 *Реферальная программа*\n"
        f"↗️Отправьте друзьям ссылку и получите бонусы\n\n"
        f"🔗 Ваша ссылка:\n{ref_link}\n\n"

        f"💎 Бонусы:\n"
        f"— За КАЖДОГО пользователя оплатившего месячную подписку: 15 дней подписки 💰БЕСПЛАТНО💰\n\n"
        f"ℹ️ Кнопка для продления подписки, "
        f"будет доступна в меню ниже, после оплаты подписки одним из пользователей\n\n"
        f"🔹Всего приглашено пользователей: {len(user.referrals)}\n"
        f"🔹Невыплаченные пользователи:\n"
        f"{list_ref_user if list_ref_user != '' else '▫️ ️️️Нет приглашенных пользователей'}"
    )
    buttons_referral = [
        InlineKeyboardButton(
            text='⏪ Назад',
            callback_data='main_menu'
        )
    ]
    if payment_status_user is not None:
        buttons_referral.insert(
            0,
            InlineKeyboardButton(
                text='🎉Получить бесплатную подписку',
                callback_data='extend_subscription_for_fifteen_days'
            )
        )
    await callback.message.answer(
        text=text,
        reply_markup=create_inline_keyboard(
            list_but=buttons_referral
        )
    )


@router.callback_query((lambda callback: callback.data.startswith("extend_device_")))
async def extend_end_subscription_device(callback: CallbackQuery):
    """Продление подписки устройства пользователем по реферальной системе"""

    device_id = callback.data[len("extend_device_"):]
    device = get_by_attribute(
        model=Devices,
        attr_name='device_id',
        attr_value=device_id
    )
    if device is None:
        await callback.message.answer(
            'Извините возникли ошибки при продлении подписки. Попробуйте позже или обратитесь в поддержу /help'
        )
        raise ValueError('Устройство не найдено')

    current_user = get_by_attribute(
        model=User,
        attr_name='telegram_id',
        attr_value=callback.message.chat.id
    )

    not_rewarded = get_rewarded_user_ids(
        referrer_user_id=current_user.user_id,
        invited_users=current_user.referrals
    )

    # TODO РЕФАКТОРИТЬ КОД ЖЕСТКО !!!
    notification_text_for_referral_system: str = ''
    for invited_user in not_rewarded:
        payments_invited_user = get_by_attribute(
            model=User,
            attr_name="user_id",
            attr_value=invited_user.user_id,
        ).payments

        if any(payment.status == 'success' for payment in payments_invited_user):
            create_object(
                model=ReferralBonus,
                bonus_receiver_id=current_user.user_id,
                invited_user_id=invited_user.user_id
            )

            # Проверяем активировано ли устройство
            if device.date_end_subscription < datetime.now():
                # получаем менеджер по управлению сервером где подключено устройство
                manager_server = Xray_api_client.getting_server_by_device(
                    device=device
                )
                # Подключаем обратно клиента
                if manager_server.enable_client(
                        client_id=device.data_connect['user_id_in_protocol'],
                        inbound_id=device.data_connect['inbound_id']
                ):
                    device.date_start_subscription = datetime.now()
                    device.date_end_subscription = datetime.now() + timedelta(days=15)
                    await callback.message.answer(
                        text='Устройство активировано'
                    )
            else:
                # Продлеваем подписку устройства на 15 дней
                device.date_end_subscription += timedelta(days=15)

            # Изменяем параметр оповещения на False, Оплата -True
            device.call_user = False
            device.payment = True
            update_attribute_object(obj=device)

            # Складываем в строку для оповещения пользователя
            notification_text_for_referral_system += (
                f'Подписка устройства успешна продлена на 15 дней за пользователя {invited_user.name}\n'
            )

    await callback.message.edit_text(
        text=notification_text_for_referral_system,
        reply_markup=create_inline_keyboard(
            list_but=[
                InlineKeyboardButton(text="⏪ Мои устройства", callback_data="my_devices"),
            ]
        )
    )
