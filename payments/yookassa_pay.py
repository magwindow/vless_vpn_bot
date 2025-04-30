import asyncio
import os
from aiogram import Bot
from sqlalchemy import select
from yookassa import Payment, Configuration
from database.models import async_session, PaymentRecord
from vless.vless_service import add_client
from dotenv import load_dotenv

load_dotenv()

Configuration.account_id = os.getenv('SHOP_ID')
Configuration.secret_key = os.getenv('YOOKASSA_API_KEY')


# Создание платежа
def create_payment(amount: float, user_id: int, tariff_key: str) -> str:
    payment = Payment.create({
        "amount": {"value": str(amount), "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "https://t.me/tadivpn_bot"},
        "capture": True,
        "description": f"Оплата тарифа {tariff_key} пользователем {user_id}",
        "metadata": {"user_id": str(user_id)}
    })

    save_payment_to_db(payment.id, user_id, tariff_key)
    return payment.confirmation.confirmation_url


# Сохраняем платеж в БД
def save_payment_to_db(payment_id: str, user_id: int, tariff_key: str):
    async def inner():
        async with async_session() as session:
            record = PaymentRecord(
                payment_id=payment_id,
                user_id=user_id,
                tariff_key=tariff_key,
                is_paid=False
            )
            session.add(record)
            await session.commit()

    asyncio.create_task(inner())


# Помечаем оплату как завершенную
def mark_payment_completed(payment_id: str):
    async def inner():
        async with async_session() as session:
            result = await session.execute(
                select(PaymentRecord).where(PaymentRecord.payment_id == payment_id)
            )
            record = result.scalar_one_or_none()
            if record:
                record.is_paid = True
                await session.commit()

    asyncio.create_task(inner())


# Генерация ключа по тарифу
async def get_tariff_key(payment_id: str):
    async with async_session() as session:
        result = await session.execute(
            select(PaymentRecord).where(PaymentRecord.payment_id == payment_id)
        )
        payment = result.scalar_one_or_none()
        if not payment:
            return None

        if payment.tariff_key == "month":
            gb = 300
            days = 30
        elif payment.tariff_key == "three_month":
            gb = 900
            days = 90
        elif payment.tariff_key == "six_month":
            gb = 2000
            days = 180
        else:
            return None

        key = await add_client(
            inbound_id=1,
            total_gb=gb,
            expiry_days=days,
            flow="xtls-rprx-vision",
            chat_id=payment.user_id,
            user_name=None
        )
        return key.access_url


# Отправка ключа пользователю после оплаты
async def check_payment_and_send_key(payment_id: str, user_id: int, bot: Bot):
    payment = Payment.find_one(payment_id)

    if payment.status == 'succeeded':
        key = await get_tariff_key(payment_id)
        if key:
            await bot.send_message(user_id, f"✅ Оплата прошла успешно! Вот ваш ключ:\n <code>{key}</code>")
            mark_payment_completed(payment_id)
