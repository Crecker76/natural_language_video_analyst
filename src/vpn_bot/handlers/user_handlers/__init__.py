from aiogram import Router

from .main_menu import router as main_menu_router
from .allocation import router as allocation_router
from .devices_management import router as devices_management_router
from .payments import router as payments_router
from .referral_system import router as referral_system_router


# Основной роутер для хэндлеров пользователя
user_router = Router()

routers = [
    main_menu_router,
    allocation_router,
    devices_management_router,
    payments_router,
    referral_system_router
]

for r in routers:
    user_router.include_router(r)

__all__ = ["user_router"]
