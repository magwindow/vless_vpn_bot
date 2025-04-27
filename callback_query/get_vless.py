from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import async_session, VlessKey
from keyboards.inline_keyboard import tariff_keyboard, main_keyboard
from vless.vless_service import add_client
from sqlalchemy import select

vless_router = Router()

INBOUND_ID = 1
FLOW = "xtls-rprx-vision"


# === Триал на 3 дня ===
@vless_router.callback_query(F.data == "trial")
async def send_trial(callback: CallbackQuery):
    user_id = callback.from_user.id

    async with async_session() as session:
        existing = await session.execute(select(VlessKey).where(VlessKey.chat_id == user_id))
        if existing.scalars().first():
            await callback.message.answer("❗️У вас уже есть активный VLESS ключ.", reply_markup=await main_keyboard())
            return

    try:
        key = await add_client(
            inbound_id=INBOUND_ID,
            total_gb=5,
            expiry_days=3,
            flow=FLOW,
            chat_id=user_id,
            user_name=callback.from_user.username
        )

        await callback.message.answer(
            f"✅ Ваш пробный VLESS ключ на 3 дня:\n\n<code>{key.access_url}</code>\n"
            f"⏳ Действителен до: {key.expires_at.strftime('%Y-%m-%d')}", reply_markup=await main_keyboard()
        )
    except Exception as e:
        await callback.message.answer(f"Ошибка: {str(e)}")


# === Обработка платных тарифов ===
# @vless_router.callback_query(F.data.in_(["month", "three_month", "six_month", "year"]))
# async def send_paid(callback: CallbackQuery):
#     user_id = callback.from_user.id
#     tariff = callback.data
#
#     tariffs = {
#         "month": {"gb": 100, "days": 30},
#         "three_month": {"gb": 300, "days": 90},
#         "six_month": {"gb": 600, "days": 180},
#         "year": {"gb": 9999, "days": 365},
#     }
#
#     try:
#         t = tariffs[tariff]
#         key = await add_client(
#             inbound_id=INBOUND_ID,
#             total_gb=t["gb"],
#             expiry_days=t["days"],
#             flow=FLOW,
#             chat_id=user_id,
#             user_name=callback.from_user.username
#         )
#
#         await callback.message.answer(
#             f"✅ Ваш VLESS ключ:\n\n<code>{key.access_url}</code>\n"
#             f"📅 Срок: до {key.expires_at.strftime('%Y-%m-%d')}", reply_markup=await tariff_keyboard()
#         )
#     except Exception as e:
#         await callback.message.answer(f"Ошибка: {str(e)}")


@vless_router.callback_query(F.data == "traffic")
async def show_tariffs(callback: CallbackQuery):
    await callback.message.edit_text(
        "💳 Выберите тариф для подключения VLESS:",
        reply_markup=await tariff_keyboard()
    )




