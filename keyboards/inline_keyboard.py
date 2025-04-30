from aiogram.utils.keyboard import InlineKeyboardBuilder


async def tariff_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ 1 месяц", callback_data="tariff_month")
    kb.button(text="🔥 3 месяца", callback_data="tariff_three_month")
    kb.button(text="🚀 6 месяцев", callback_data="tariff_six_month")
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(1)
    return kb.as_markup()


async def back():
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(1)
    return kb.as_markup()


async def paid_keyboard(tariff_key: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Оплатить картой", callback_data=f"pay_{tariff_key}")
    kb.button(text="💰 Криптовалюта", callback_data=f"crypto_{tariff_key}")
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(1)
    return kb.as_markup()


async def check_pay():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Проверить оплату", callback_data="check_payment")
    kb.button(text='Назад', callback_data='back_main')
    return kb.as_markup()


async def help_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Подключить iOS/MacOS🍏", url="https://telegra.ph/Podklyuchenie-v2raytun-iOS-11-09")
    kb.button(text="Подключить Android🤖", url="https://telegra.ph/Podklyuchenie-v2RayTun-Android-11-09")
    kb.button(text="Подключить Windows🖥", url="https://telegra.ph/Nastrojka-VPN-PK-Windows-08-08")
    kb.button(text="🆘 Поддержка", url="https://t.me/magwindow")
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(1)
    return kb.as_markup()


async def connect_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Скачать для IOS/MacOS🍏",
              url="https://apps.apple.com/ru/app/v2raytun/id6476628951")
    kb.button(text="Скачать для Android📱",
              url="https://play.google.com/store/apps/details?id=com.v2raytun.android&hl=ru&gl=US")
    kb.button(text="Скачать для Windows💻",
              url="https://github.com/hiddify/hiddify-next/releases/latest/download/Hiddify-Windows-Setup-x64.exe")
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(1)
    return kb.as_markup()
