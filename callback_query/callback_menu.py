from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.models import async_session, VlessKey
from sqlalchemy import select
from invite_friends import handle_invite
from keyboards.inline_keyboard import main_keyboard

router_call = Router()


@router_call.callback_query(F.data == 'invite_friend')
async def invite_friend_callback(call: CallbackQuery):
    await call.answer()  # убирает "часики"
    await handle_invite(call.message)


@router_call.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await callback.message.edit_text(
        "Если у вас возникли вопросы или проблемы — напишите в нашу техподдержку 👇",
        reply_markup=await main_keyboard()
    )


@router_call.callback_query(F.data == "back_main")
async def back_to_main_menu(call: CallbackQuery):
    await call.message.delete()


@router_call.callback_query(F.data == "my_keys")
async def show_user_keys(call: CallbackQuery):
    user_id = call.from_user.id

    async with async_session() as session:
        result = await session.execute(
            select(VlessKey).where(VlessKey.chat_id == user_id)
        )
        keys = result.scalars().all()

    if not keys:
        await call.message.edit_text("🔑 У вас пока нет активных ключей.")
        return

    text = "🔑 Ваши VLESS ключи:\n\n"
    for idx, key in enumerate(keys, 1):
        expires = key.expires_at.strftime("%d-%m-%Y") if key.expires_at else "∞"
        text += f"{idx}. <code>{key.access_url}</code>\n📅 Действителен до: {expires}\n\n"

    await call.message.edit_text(text, reply_markup=await main_keyboard())