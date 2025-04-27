from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline_keyboard import paid_keyboard

tariff_router = Router()


@tariff_router.callback_query(F.data == "month")
async def tariff_month(callback: CallbackQuery):
    await callback.message.answer("👌 Доступ: 1 месяц", reply_markup=await paid_keyboard())


@tariff_router.callback_query(F.data == "three_month")
async def tariff_three_month(callback: CallbackQuery):
    await callback.message.answer("⚡️ Доступ: 3 месяца", reply_markup=await paid_keyboard())


@tariff_router.callback_query(F.data == "six_month")
async def tariff_six_month(callback: CallbackQuery):
    await callback.message.answer("🔥 Доступ: 6 месяцев", reply_markup=await paid_keyboard())
