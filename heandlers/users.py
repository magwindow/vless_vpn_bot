import os
import requests
from database.models import add_user_if_not_exists
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from keyboards.inline_keyboard import tariff_keyboard, help_keyboard, connect_keyboard, back
from keyboards.reply_menu_keyboard import menu

router_users: Router = Router()


@router_users.message(CommandStart())
async def start_command(message: Message):
    await add_user_if_not_exists(message.from_user.id, message.from_user.username)
    await message.answer(
        text='👋🏻 Привет!\n\nЭто Telegram-бот для подключения к VPN.\n\nДоступны локации:\n'
             '├ 🇫🇮 Финляндия\n├ 🇷🇺 Россия\n├ 🇹🇷 Турция\n├ 🇳🇱 Нидерланды\n└ 🇷🇴 Румыния\n\n'
             'По всем вопросам: <a href="https://t.me/magwindow">magwindow</a>\n'
             'Для начала работы нажмите ⚡️Подключиться ↓',
        reply_markup=menu,
        disable_web_page_preview=True
    )


# Хендлер на кнопку "Купить"
@router_users.message(F.text == '🔥 Купить')
async def buy_tariff(message: Message):
    await message.delete()
    await message.answer(
        text="Для полного доступа выберите удобный для вас тариф:\n\n"
             "250₽ / 1 мес\n"
             "650₽ / 3 мес\n"
             "1200₽ / 6 мес\n\n"
             "💳 Можно оплатить через:\n"
             "SberPay, СБП, T-Pay, карты и криптовалюты.",
        reply_markup=await tariff_keyboard()
    )


# Хендлер на кнопку "Помощь"
@router_users.message(F.text == '❓ Помощь')
async def help_command(message: Message):
    await message.delete()
    await message.answer(
        text="Если у вас проблемы с подключением, отправьте статус из бота\n"
             " и скриншот из приложения, которым вы пользуетесь для\n"
             " доступа к VPN в поддержку.\n\n"
             "Ниже представлены инструкции для подключения к сервису ↓",
        reply_markup=await help_keyboard()
    )


# Хендлер на кнопку "Подключиться"
@router_users.message(F.text == '⚡️ Подключиться!')
async def connect_command(message: Message):
    await message.delete()
    await message.answer(
        text="Доступ к VPN в 2 шага:\n\n"
             "1️⃣ <b>Скачать</b> - для скачивания приложения\n"
             "2️⃣ <b>Подключить</b> - для добавления подписки\n\n"
             "Настроить VPN вручную:\n"
             '<a href="https://telegra.ph/Podklyuchenie-v2RayTun-Android-11-09">Инструкция для Android</a>"\n'
             '<a href="https://telegra.ph/Podklyuchenie-v2raytun-iOS-11-09">Инструкция для iOS/MacOS</a>\n'
             '<a href="https://telegra.ph/Nastrojka-VPN-PK-Windows-08-08">Инструкция для Windows</a>\n\n'
             "Ссылка для ручного подключения\n"
             "Тапните чтобы скопировать в буфер обмена ↓",
        reply_markup=await connect_keyboard(),
        disable_web_page_preview=True
    )


# Хендлер на кнопку "Статус"
@router_users.message(F.text == 'ℹ️ Статус')
async def status_command(message: Message):
    await message.delete()
    url = "https://raw.githubusercontent.com/magwindow/vless_vpn_bot/refs/heads/master/images/status.jpg"
    local_path = "status.jpg"

    # Проверяем, существует ли файл
    if not os.path.exists(local_path):
        response = requests.get(url)
        with open(local_path, "wb") as file:
            file.write(response.content)

    # Теперь отправляем локальный файл
    photo = FSInputFile(local_path)

    await message.answer_photo(photo,
                               caption="Доступ:☑️<b>Пробный период</b>\n"
                                       "├ Осталось дней: <b>9</b>\n"
                                       "└ Активна до: <b>07.05.2025 09:30</b>\n\n"
                                       "<b>Ваша партнерская ссылка:</b>\n"
                                       "<code>https://t.me/testvpn121231_bot?start=ref_123456789</code>\n\n"
                                       "Нажмите на неё, чтобы скопировать и отправьте друзьям!\n\n"
                                       "<b>Приведено друзей:</b>\n"
                                       "└ Всего - 0, Оплачивают - 0",
                               reply_markup=await back()
                               )
