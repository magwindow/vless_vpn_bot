from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import select

from database.models import async_session, PaymentRecord
from keyboards.inline_keyboard import paid_keyboard, check_pay
from payments.yookassa_pay import create_payment, check_payment_and_send_key

tariff_router = Router()

# Тарифы и их цены
TARIFF_PRICES = {
    "month": 250.00,
    "three_month": 650.00,
    "six_month": 1200.00
}


# Выбор тарифа → показать кнопки оплаты
@tariff_router.callback_query(F.data.startswith("tariff_"))
async def select_tariff(callback: CallbackQuery):
    tariff_key = callback.data.split("_", 1)[1]  # 'month', 'three_month', 'six_month'

    titles = {
        "month": "👌 Доступ: 1 месяц",
        "three_month": "⚡️ Доступ: 3 месяца",
        "six_month": "🔥 Доступ: 6 месяцев"
    }

    text = titles.get(tariff_key, "Выбран тариф")
    await callback.message.answer(text, reply_markup=await paid_keyboard(tariff_key))


# Оплата по тарифу → создать ссылку
@tariff_router.callback_query(F.data.startswith("pay_"))
async def pay_tariff(callback: CallbackQuery):
    tariff_key = callback.data.split("_", 1)[1]

    amount = TARIFF_PRICES.get(tariff_key)
    if amount is None:
        await callback.message.answer("Ошибка: неизвестный тариф.")
        return

    payment_url = create_payment(amount, callback.from_user.id, tariff_key)
    await callback.message.answer(
        f"💸 Перейди по ссылке для оплаты:\n{payment_url}",
        reply_markup= await check_pay(),
        disable_web_page_preview=True
    )


@tariff_router.callback_query(F.data == "check_payment")
async def manual_check(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with async_session() as session:
        result = await session.execute(
            select(PaymentRecord).where(
                PaymentRecord.user_id == user_id,
                PaymentRecord.is_paid == False
            ).order_by(PaymentRecord.id.desc()).limit(1)
        )
        payment_record = result.scalar_one_or_none()

    if payment_record:
        await check_payment_and_send_key(payment_record.payment_id, user_id, callback.bot)
        await callback.answer("Проверяю оплату...", show_alert=False)
    else:
        await callback.message.answer("❗️Не найдено неоплаченных платежей.")
