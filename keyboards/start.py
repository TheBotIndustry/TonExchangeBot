from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def starting_keyboard():
    key = ReplyKeyboardMarkup(resize_keyboard=True)
    key.add(
        KeyboardButton("🔄 Обмен"),
        KeyboardButton("💎 Мой профиль")
    )
    key.add(
        KeyboardButton("🔷 О нас")
    )
    return key
