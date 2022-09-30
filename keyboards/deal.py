from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from loader import database
from utils.other.operations_with_cryptocurrency import spaceAmount


async def deal_cryptocurrency_keyboard():
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton('💎 TON', callback_data='dealCryptocurrency_TON'),
    )
    key.add(
        InlineKeyboardButton('⬅ Назад', callback_data='back_to_exchange')
    )
    return key


async def deal_currency_keyboard(market_is_sell):
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton('RUB', callback_data='dealCurrency_RUB'),
        InlineKeyboardButton('USD', callback_data='dealCurrency_USD')
    )
    key.add(
        InlineKeyboardButton('⬅ Назад', callback_data='cripto_sell' if market_is_sell == True else 'cripto_buy')
    )
    return key


async def deal_notCategories_keyboard(cryptocurrency):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("➕ Создать объявление", callback_data="createAdvert"),
        InlineKeyboardButton("⬅ Назад", callback_data=f"dealCryptocurrency_{cryptocurrency}"),
    )
    return key


async def deal_categories_keyboard(cryptocurrency, categories_dict):
    key = InlineKeyboardMarkup(row_width=1)
    for category_id in categories_dict:
        category = await database.get_category(category_id)
        key.add(
            InlineKeyboardButton(f"{category.name} ({categories_dict.get(category_id)})",
                                 callback_data=f"dealCategory_{category.id}")
        )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"dealCryptocurrency_{cryptocurrency}")
    )
    return key


async def deal_subcategories_keyboard(currency, subcategories_dict):
    key = InlineKeyboardMarkup(row_width=1)
    for subcategory_id in subcategories_dict:
        subcategory = await database.get_subcategory(subcategory_id)
        key.add(
            InlineKeyboardButton(f"{subcategory.name} ({subcategories_dict.get(subcategory_id)})",
                                 callback_data=f"dealSubcategory_{subcategory.id}")
        )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"dealCurrency_{currency}")
    )
    return key


async def deal_adverts_keyboard(category_id, adverts, currency, user_id, filterAdvertAmount, filterAdvertCount):
    key = InlineKeyboardMarkup(row_width=1)
    if filterAdvertAmount:
        key.row(
            InlineKeyboardButton(f"🔎 {filterAdvertCount} {filterAdvertAmount}", callback_data="FilterSetDealAdvert"),
            InlineKeyboardButton("❌ Сбросить", callback_data="FilterResetDealAdvert")
        )
    else:
        key.add(
            InlineKeyboardButton("🔎 Фильтр по сумме", callback_data="FilterSetDealAdvert")
        )
    for advert in adverts:
        advert_model = advert['advert']
        button_name = "t"
        if currency == "USD":
            button_name = f"${await spaceAmount(advert['price'])} | {advert_model.limitLow}-{advert_model.limitHigh} {advert_model.cryptocurrency}"
        elif currency == "RUB":
            button_name = f"{await spaceAmount(advert['price'])} ₽ | {advert_model.limitLow}-{advert_model.limitHigh} {advert_model.cryptocurrency}"
        key.add(
            InlineKeyboardButton("🔷 " + button_name if advert_model.user_id == user_id else button_name,
                                 callback_data=f"myAdvert_{advert_model.id}" if advert_model.user_id == user_id else f"dealAdvert_{advert_model.id}")
        )
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"dealCategory_{category_id}")
    )
    return key


async def deal_start_keyboard(advert_id, subcategory_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("💼 Начать сделку", callback_data=f"makeDeal_{advert_id}"),
        InlineKeyboardButton("⬅ Назад", callback_data=f"dealSubcategory_{subcategory_id}"),
    )
    return key


async def filter_advert_amount_keyboard(different_select):
    key = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    key.add(
        KeyboardButton(f"Указать в {different_select}"),
        KeyboardButton("❌ Отменить")
    )
    return key


async def deal_back_keyboard(different_select):
    key = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    key.add(
        KeyboardButton(f"Ввести в {different_select}"),
        KeyboardButton("⬅ Назад")
    )
    return key


async def accept_make_deal_keyboard(advert_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("✅ Да", callback_data="areYouSure?"),
        InlineKeyboardButton("⬅ Нет", callback_data=f"dealAdvert_{advert_id}")
    )
    return key


async def createDealCreator_keyboard(deal_id):
    key = InlineKeyboardMarkup()
    key.add(
        InlineKeyboardButton("❌ Отменить сделку", callback_data=f"cancelDealCreate {deal_id}")
    )
    return key


async def createDealContrAgent_keyboard(deal_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("✅ Согласиться", callback_data=f"startDealCreate {deal_id}"),
        InlineKeyboardButton("❌ Отказаться", callback_data=f"cancelDealCreate {deal_id}"),
    )
    return key


async def send_payment_deal_keyboard(advert_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("⬅ Назад", callback_data=f"backToDealAdvert_{advert_id}")
    )
    return key


async def send_payment_creator_deal_keyboard(deal_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("❌ Отказаться", callback_data=f"cancelDealCreate {deal_id}")
    )
    return key


async def confirm_send_payment_creator_deal_keyboard(deal_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("✅ Всё верно", callback_data=f"confirmCreatorPaymentDeal {deal_id}"),
        InlineKeyboardButton("🔃 Поменять реквизиты", callback_data=f"changeCreatorPaymentDeal {deal_id}"),
        InlineKeyboardButton("❌ Отказаться от сделки", callback_data=f"cancelDealCreate {deal_id}")
    )
    return key


async def confirm_transfer_user_deal_keyboard(deal_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("✅ Перевод сделан", callback_data=f"confirmTransferUserDeal {deal_id}"),
        InlineKeyboardButton("❌ Отказаться от сделки", callback_data=f"cancelDealCreate {deal_id}")
    )
    return key


async def confirm_transfer_creator_deal_keyboard(deal_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("✅ Перевод получен", callback_data=f"confirmTransferCreatorDeal {deal_id}"),
        InlineKeyboardButton("⚖ Перевод не получен (Арбитраж)", callback_data=f"arbitrDeal {deal_id}")
    )
    return key


async def yes_confirm_transfer_creator_deal_keyboard(deal_id):
    key = InlineKeyboardMarkup(row_width=1)
    key.add(
        InlineKeyboardButton("✅ Уверен", callback_data=f"yesConfirmTransferCreatorDeal {deal_id}"),
        InlineKeyboardButton("⚖ Перевод не получен (Арбитраж)", callback_data=f"arbitrDeal {deal_id}")
    )
    return key
