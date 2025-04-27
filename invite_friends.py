import os
from keyboards.inline_keyboard import main_keyboard
from aiogram.types import Message
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


async def handle_invite(message: Message):
    bot_username = os.getenv("BOT_USERNAME")
    user_id = message.from_user.id
    invite_url = f"https://t.me/{bot_username}?start={user_id}"

    await message.answer(
        f"🔗 Пригласи друга и получи бонус!\n"
        f"Просто отправь ему эту ссылку:\n\n{invite_url}",
        reply_markup=await main_keyboard()
    )


