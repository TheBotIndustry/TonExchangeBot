from aiogram.utils.exceptions import MessageNotModified

from loader import dp


@dp.errors_handler(exception=MessageNotModified)
async def skip_errors_handler(update, exception):
    return True
