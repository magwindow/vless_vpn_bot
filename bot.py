import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from callback_query.callback_menu import router_call
from callback_query.callback_payments import tariff_router
from callback_query.get_vless import vless_router
from heandlers.users import router_users
from database.models import init_models
from middlewares.register_user import RegisterUserMiddleware
from states.admin_promo import router_admin

# Загрузка переменных окружения
load_dotenv(find_dotenv())

# Создание бота
bot: Bot = Bot(
    token=os.getenv('BOT_TOKEN'),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


async def startup(dispatcher: Dispatcher):
    await init_models()  # Инициализация моделей БД
    print('Bot is started!')


async def shutdown(dispatcher: Dispatcher):
    print('Bot is shutting down...')


async def main():
    dp = Dispatcher()

    # Подключаем middleware ДО роутеров
    dp.message.middleware(RegisterUserMiddleware())
    dp.callback_query.middleware(RegisterUserMiddleware())

    # Подключаем роутеры
    dp.include_router(router_users)
    dp.include_router(router_admin)
    dp.include_router(router_call)
    dp.include_router(vless_router)
    dp.include_router(tariff_router)

    # Подключаем события старта/остановки
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())