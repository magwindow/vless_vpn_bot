from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.models import PromoCode, async_session
from tg_admin import ADMIN_IDS

router_admin = Router()


class CreatePromo(StatesGroup):
    waiting_for_code = State()
    waiting_for_total_gb = State()
    waiting_for_expiry_days = State()


@router_admin.message(F.text == "/create_promo")
async def create_promo_command(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет прав использовать эту команду.")
        return

    await message.answer("Введите название промокода:")
    await state.set_state(CreatePromo.waiting_for_code)


@router_admin.message(CreatePromo.waiting_for_code)
async def promo_code_entered(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    await message.answer("Введите сколько ГБ трафика давать по промокоду:")
    await state.set_state(CreatePromo.waiting_for_total_gb)


@router_admin.message(CreatePromo.waiting_for_total_gb)
async def promo_gb_entered(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❗️ Введите число.")
        return

    await state.update_data(total_gb=int(message.text))
    await message.answer("Введите срок действия ключа в днях:")
    await state.set_state(CreatePromo.waiting_for_expiry_days)


@router_admin.message(CreatePromo.waiting_for_expiry_days)
async def promo_days_entered(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❗️ Введите число.")
        return

    await state.update_data(expiry_days=int(message.text))
    data = await state.get_data()
    print(data)

    async with async_session() as session:
        # Проверка на уникальность промокода
        existing = await session.execute(select(PromoCode).filter_by(code=data['code']))
        if existing.scalar_one_or_none():
            await message.answer("❗️ Такой промокод уже существует.")
            await state.clear()
            return

        promo = PromoCode(
            code=data['code'],
            total_gb=data['total_gb'],
            expiry_days=data['expiry_days']
        )
        session.add(promo)
        await session.commit()

    await message.answer(f"✅ Промокод {data['code']} создан!\n"
                         f"Трафик: {data['total_gb']} ГБ\n"
                         f"Срок действия: {data['expiry_days']} дней")
    await state.clear()
