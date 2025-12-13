from aiogram import Router


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
