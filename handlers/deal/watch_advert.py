from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.deal import deal_start_keyboard
from loader import dp, database
from utils.other.operations_with_cryptocurrency import spaceAmount


@dp.callback_query_handler(text_startswith="dealAdvert_", state="*")
async def dealAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    advert = await database.get_advert(advert_id)
    buy_or_sell_text = "купить" if advert.is_sell == True else "продать"
    select_payment_text = "отправки" if advert.is_sell == True else "получения"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    course = await database.get_course(advert.cryptocurrency)
    course_text = ""
    if advert.fixPrice:
        if advert.currency == "USD":
            course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))}'
        elif advert.currency == "RUB":
            course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽'
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    key = await deal_start_keyboard(advert_id, subcategory.id)
    await call.message.edit_text(f"Вы можете <b>{buy_or_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                 f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                 f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}\n"
                                 f"<b>∙ Мин-макс сумма сделки:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                                 f"{comment_text}", reply_markup=key)


@dp.callback_query_handler(text_startswith="backToDealAdvert_", state="*")
async def backToDealAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    deal_id = data.get('deal_id')
    if deal_id is not None:
        deal = await database.get_deal(deal_id)
        if deal is not None:
            if deal.is_sell and deal.user_id == call.message.chat.id:
                await database.delete_deal(deal_id)
                await database.get_back_deposit(call.message.chat.id, deal.cryptocurrency, deal.amount_crypto)
    advert_id = call.data.split("_")[1]
    advert = await database.get_advert(advert_id)
    buy_or_sell_text = "купить" if advert.is_sell == True else "продать"
    select_payment_text = "отправки" if advert.is_sell == True else "получения"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    course = await database.get_course(advert.cryptocurrency)
    course_text = ""
    if advert.fixPrice:
        if advert.currency == "USD":
            course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))}'
        elif advert.currency == "RUB":
            course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽'
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    key = await deal_start_keyboard(advert_id, subcategory.id)
    await call.message.edit_text(f"Вы можете <b>{buy_or_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                 f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                 f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}\n"
                                 f"<b>∙ Мин-макс сумма сделки:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                                 f"{comment_text}", reply_markup=key)
