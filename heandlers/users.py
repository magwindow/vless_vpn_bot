import logging
import os
import requests
from database.models import add_user_if_not_exists, User, async_session
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from datetime import datetime, timedelta
from sqlalchemy import select

from keyboards.inline_keyboard import tariff_keyboard, help_keyboard, connect_keyboard, back
from keyboards.reply_menu_keyboard import menu

logging.basicConfig(level=logging.INFO)

BOT_USERNAME = os.getenv('BOT_USERNAME')

router_users: Router = Router()


# Старт с обработкой рефералов
@router_users.message(CommandStart())
async def start_command(message: Message):
    ref_id = None

    if message.text and " " in message.text:
        parts = message.text.split()
        if len(parts) > 1 and parts[1].startswith("ref_"):
            ref_id = int(parts[1][4:])

    await add_user_if_not_exists(
        user_id=message.from_user.id,
        username=message.from_user.username,
        ref_id=ref_id,
        is_paid=False,
    )

    # Если есть реферальный ID, добавляем пользователя как реферала
    if ref_id:
        async with async_session() as session:
            # Проверяем, существует ли реферер с этим ID
            result = await session.execute(select(User).filter_by(id=ref_id))
            referrer = result.scalar_one_or_none()
            if referrer:
                # Устанавливаем ID реферера у текущего пользователя
                user = await session.execute(select(User).filter_by(id=message.from_user.id))
                current_user = user.scalar_one_or_none()
                if current_user:
                    current_user.referrer_id = ref_id
                    session.add(current_user)
                    await session.commit()

                referrer.referral_count += 1
                session.add(referrer)
                await session.commit()

    await message.answer(
        text='👋🏻 Привет!\n\nЭто Telegram-бот для подключения к VPN.\n\nДоступны локации:\n'
             '├ 🇫🇮 Финляндия\n├ 🇷🇺 Россия\n├ 🇹🇷 Турция\n├ 🇳🇱 Нидерланды\n└ 🇷🇴 Румыния\n\n'
             'По всем вопросам: <a href="https://t.me/magwindow">magwindow</a>\n'
             'Для начала работы нажмите ⚡️Подключиться ↓\n\n'
             'Введите промо-код в чате бота, чтобы получить бесплатный доступ 🎁',
        reply_markup=menu,
        disable_web_page_preview=True
    )


# Купить
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


# Помощь
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


# Подключиться
@router_users.message(F.text == '⚡️ Подключиться!')
async def connect_command(message: Message):
    await message.delete()
    await message.answer(
        text="Доступ к VPN в 2 шага:\n\n"
             "1️⃣ <b>Скачать</b> - для скачивания приложения\n"
             "2️⃣ <b>Подключить</b> - для добавления подписки\n\n"
             "Настроить VPN вручную:\n"
             '<a href="https://telegra.ph/Podklyuchenie-v2RayTun-Android-11-09">Инструкция для Android</a>\n'
             '<a href="https://telegra.ph/Podklyuchenie-v2raytun-iOS-11-09">Инструкция для iOS/MacOS</a>\n'
             '<a href="https://telegra.ph/Nastrojka-VPN-PK-Windows-08-08">Инструкция для Windows</a>\n\n'
             "Ссылка для ручного подключения\n"
             "Тапните чтобы скопировать в буфер обмена ↓",
        reply_markup=await connect_keyboard(),
        disable_web_page_preview=True
    )


# Статус
@router_users.message(F.text == 'ℹ️ Статус')
async def status_command(message: Message):
    await message.delete()

    url = "https://raw.githubusercontent.com/magwindow/vless_vpn_bot/refs/heads/master/images/status.jpg"
    local_path = "status.jpg"

    # Скачиваем картинку, если её ещё нет
    if not os.path.exists(local_path):
        response = requests.get(url)
        with open(local_path, "wb") as file:
            file.write(response.content)

    photo = FSInputFile(local_path)

    # Подключаемся к БД
    async with async_session() as session:
        # Считаем количество рефералов
        result = await session.execute(
            select(User).where(User.referrer_id == message.from_user.id)
        )
        referrals = result.scalars().all()
        referral_count = len(referrals)
        # Считаем оплаченных рефералов (если у тебя нет поля is_paid - будет просто 0)
        # paid_referral_count = len([r for r in referrals if getattr(r, "is_paid", False)])
        paid_referral_count = len([r for r in referrals if r.is_paid])

    # Здесь я просто симулирую пробный период
    trial_end_date = datetime.utcnow() + timedelta(days=3)
    remaining_days = (trial_end_date - datetime.utcnow()).days

    await message.answer_photo(
        photo,
        caption=f"Доступ:☑️ <b>Пробный период</b>\n"
                f"├ Осталось дней: <b>{remaining_days}</b>\n"
                f"└ Активна до: <b>{trial_end_date.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
                f"<b>Ваша партнёрская ссылка:</b>\n"
                f"<code>https://t.me/{BOT_USERNAME}?start=ref_{message.from_user.id}</code>\n\n"
                f"Нажмите на неё, чтобы скопировать и отправьте друзьям!\n\n"
                f"<b>Приведено друзей:</b>\n"
                f"└ Всего - {referral_count}, Оплачивают - {paid_referral_count}",
        reply_markup=await back(),
        disable_web_page_preview=True
    )
