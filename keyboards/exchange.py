from typing import List, Dict

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import database
from utils.database_api.models.adverts import Adverts
from utils.other.operations_with_cryptocurrency import makeRoundFloatTON, spaceAmount


async def exchange_keyboard(data: Dict):
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton("📥 Купить", callback_data="cripto_buy"),
        InlineKeyboardButton("📤 Продать", callback_data="cripto_sell"),
    )
    if data.get('market_text'):
        key.add(
            InlineKeyboardButton("👀 Продолжить просмотр", callback_data="continueWatchAdvert")
        )
    key.row(
        InlineKeyboardButton("🗒 Мои объявления", callback_data="myAdverts")
    )
    return key


async def my_adverts_keyboard(adverts_list: List[Adverts], data: Dict):
    key = InlineKeyboardMarkup(row_width=1)
    key.row(
        InlineKeyboardButton("⭕ Все" if data.get('filterMyAdvert') == "All" else "⚪ Все",
                             callback_data="filterMyAdvert_All"),
        InlineKeyboardButton("⭕ Покупка" if data.get('filterMyAdvert') == "Buy" else "⚪ Покупка", callback_data="filterMyAdvert_Buy"),
        InlineKeyboardButton("⭕ Продажа" if data.get('filterMyAdvert') == "Sell" else "⚪ Продажа", callback_data="filterMyAdvert_Sell")
    )
    for advert in adverts_list:
        my_course_text = ""
        if advert.fixPrice:
            if advert.currency == "USD":
                my_course_text = f"${advert.fixPrice}"
            elif advert.currency == "RUB":
                my_course_text = f"{advert.fixPrice} ₽"
        else:
            course = await database.get_course(advert.cryptocurrency)
            my_percent = 100 - advert.percent if advert.decimalPercent == "-" else 100 + advert.percent
            if advert.currency == "USD":
                my_course_text = f"${await spaceAmount(round(course.course / 100 * my_percent, 2))}"
            elif advert.currency == "RUB":
                my_course_text = f"{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽"
        advert_status = "✅" if advert.status else "🚫"
        if advert.cryptocurrency == "TON":
            button_name = f"{advert_status} Покупаю от {await makeRoundFloatTON(advert.limitLow)} до {await makeRoundFloatTON(advert.limitHigh)} {advert.cryptocurrency} за {my_course_text}" if not advert.is_sell else f"{advert_status} Продаю от {await makeRoundFloatTON(advert.limitLow)} до {await makeRoundFloatTON(advert.limitHigh)} {advert.cryptocurrency} за {my_course_text}"
        key.add(
            InlineKeyboardButton(button_name, callback_data=f'myAdvert_{advert.id}')
        )
    key.add(
        InlineKeyboardButton('➕ Создать объявление', callback_data="createAdvert")
    )
    if data.get('is_sell_original'):
        key.add(
            InlineKeyboardButton("🔜 Продолжить создание...", callback_data="continueCreateAdvert")
        )
    key.add(
        InlineKeyboardButton('⬅ Назад', callback_data='back_to_exchange')
    )
    return key


async def create_advert_is_sell_keyboard():
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton("Продать", callback_data="createAdvertIsSell_Sell"),
        InlineKeyboardButton("Купить", callback_data="createAdvertIsSell_Buy"),
    )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data='myAdverts')
    )
    return key


async def create_advert_cryptocurrency_keyboard():
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton("💎 TON", callback_data="createAdvertCryptocurrency_TON"),
    )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data='createAdvert')
    )
    return key


async def create_advert_currency_keyboard(is_sell):
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton("RUB", callback_data='createAdvertCurrency_RUB'),
        InlineKeyboardButton("USD", callback_data='createAdvertCurrency_USD')
    )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f'createAdvertIsSell_{is_sell}')
    )
    return key


async def create_advert_category_keyboard(cryptocurrency, currency):
    key = InlineKeyboardMarkup(row_width=2)
    categories = await database.get_all_categories(currency)
    for category in categories:
        key.add(
            InlineKeyboardButton(category.name, callback_data=f'createAdvertCategory_{category.id}')
        )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f'createAdvertCryptocurrency_{cryptocurrency}')
    )
    return key


async def create_advert_subcategory_keyboard(currency, category_id):
    key = InlineKeyboardMarkup(row_width=2)
    subcategories = await database.get_all_subcategories(category_id)
    for subcategory in subcategories:
        key.add(
            InlineKeyboardButton(subcategory.name, callback_data=f'createAdvertSubategory_{subcategory.id}')
        )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f'createAdvertCurrency_{currency}')
    )
    return key


async def create_advert_price_keyboard(category_id):
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f'createAdvertCategory_{category_id}')
    )
    return key


async def create_advert_limit_keyboard(subcategory_id):
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f'createAdvertSubategory_{subcategory_id}')
    )
    return key


async def create_advert_comment_keyboard():
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("📵 Без комментария", callback_data="createAdvertWithoutComment"),
        InlineKeyboardButton("⬅ Назад", callback_data='createAdvertCourse')
    )
    return key


async def create_advert_edit_keyboard(advert_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("✏ Редактировать объявление", callback_data=f"myAdvert_{advert_id}"),
        InlineKeyboardButton("🗒 Мои объявления", callback_data="myAdverts")
    )
    return key
