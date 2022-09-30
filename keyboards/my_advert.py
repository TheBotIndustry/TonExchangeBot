from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import database


async def my_advert_keyboard(advert_id, data):
    key = InlineKeyboardMarkup(row_width=1)
    advert = await database.get_advert(advert_id)
    key.row(
        InlineKeyboardButton("✏ Курс", callback_data=f"myAdvertChangeCourse_{advert_id}"),
        InlineKeyboardButton("✏ Лимиты", callback_data=f"myAdvertChangeLimit_{advert_id}")
    )
    key.add(
        InlineKeyboardButton("✏ Комментарий" if advert.comment else "➕ Комментарий", callback_data=f"myAdvertChangeComment_{advert_id}"),
        InlineKeyboardButton("🚫 Выключить объявление" if advert.status else "✅ Включить объявление", callback_data=f"myAdvertChangeStatus_{advert_id}"),
        InlineKeyboardButton("🗑 Удалить объявление", callback_data=f"myAdvertDelete_{advert_id}")
    )
    if data.get('selectExchange') and data.get('market_subcategory_id'):
        key.add(
            InlineKeyboardButton("⬅ Назад", callback_data=f"dealSubcategory_{data['market_subcategory_id']}")
        )
    else:
        key.add(
            InlineKeyboardButton("⬅ Назад", callback_data="myAdverts")
        )
    return key


async def back_my_advert_keyboard(advert_id, data):
    key = InlineKeyboardMarkup(row_width=1)
    advert = await database.get_advert(advert_id)
    key.row(
        InlineKeyboardButton("✏ Курс", callback_data=f"myAdvertChangeCourse_{advert_id}"),
        InlineKeyboardButton("✏ Лимиты", callback_data=f"myAdvertChangeLimit_{advert_id}")
    )
    key.add(
        InlineKeyboardButton("✏ Комментарий" if advert.comment else "➕ Комментарий", callback_data=f"myAdvertChangeComment_{advert_id}"),
        InlineKeyboardButton("🚫 Выключить объявление" if advert.status else "✅ Включить объявление", callback_data=f"myAdvertChangeStatus_{advert_id}"),
        InlineKeyboardButton("🗑 Удалить объявление", callback_data=f"myAdvertDelete_{advert_id}")
    )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"dealSubcategory_{data['market_subcategory_id']}")
    )
    return key


async def my_advert_course_limit_keyboard(advert_id):
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"myAdvert_{advert_id}")
    )
    return key


async def my_advert_course_comment_keyboard(advert_id):
    advert = await database.get_advert(advert_id)
    key = InlineKeyboardMarkup(row_width=1)
    if advert.comment:
        key.add(
            InlineKeyboardButton("➖ Удалить комментарий", callback_data=f"myAdvertDeleteComment_{advert_id}")
        )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"myAdvert_{advert_id}")
    )
    return key


async def my_advert_delete_keyboard(advert_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("🗑 Удалить объявление", callback_data=f"myAdvertAcceptDelete_{advert_id}"),
        InlineKeyboardButton("⬅ Назад", callback_data=f"myAdvert_{advert_id}")
    )
    return key
