from aiogram.utils.keyboard import InlineKeyboardBuilder


async def main_keyboard():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Быстрая инструкция 📖', callback_data='manual')
    keyboard_builder.button(text='Получить ключ 🔑', callback_data='trial')
    keyboard_builder.button(text='Тарифы 🔐', callback_data='traffic')
    keyboard_builder.button(text='Мои ключи 🧩', callback_data='my_keys')
    keyboard_builder.button(text="💬 Техподдержка", url="https://t.me/vlessvpn24_support")
    keyboard_builder.button(text='➕Пригласить друга', callback_data='invite_friend')

    keyboard_builder.adjust(1, 2, 2)
    return keyboard_builder.as_markup()


async def tariff_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ 1 месяц", callback_data="month")
    kb.button(text="🔥 3 месяца", callback_data="three_month")
    kb.button(text="🚀 6 месяцев", callback_data="six_month")
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(1)
    return kb.as_markup()


async def back():
    kb = InlineKeyboardBuilder()
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(1)
    return kb.as_markup()


async def paid_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Оплатить!", url="https://yookassa.com")
    kb.button(text="Оплатить криптовалютой!", url="https://crypto.com")
    kb.button(text='Назад', callback_data='back_main')
    kb.adjust(1)
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
