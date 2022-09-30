from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def profile_keyboard(hide=None):
    key = InlineKeyboardMarkup()
    if hide is None:
        key.add(
            InlineKeyboardButton("⬇ Больше информации", callback_data="more_information")
        )
    else:
        key.add(
            InlineKeyboardButton("⬆ Меньше информации", callback_data="less_information")
        )
    key.row(
        InlineKeyboardButton("Пополнить", callback_data="topup"),
        InlineKeyboardButton("Вывести", callback_data="withdraw")
    )
    return key
