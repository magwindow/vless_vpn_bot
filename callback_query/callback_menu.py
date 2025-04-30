from aiogram import Router, F
from aiogram.types import CallbackQuery


router_call = Router()


@router_call.callback_query(F.data == "back_main")
async def back_to_main_menu(call: CallbackQuery):
    await call.message.delete()



