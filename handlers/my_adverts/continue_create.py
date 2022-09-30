from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.my_adverts.create_advert import CreateAdvertStatesGroup
from keyboards.exchange import create_advert_limit_keyboard, create_advert_price_keyboard, \
    create_advert_subcategory_keyboard, create_advert_category_keyboard, create_advert_currency_keyboard, \
    create_advert_cryptocurrency_keyboard, create_advert_comment_keyboard
from loader import dp, database
from utils.other.operations_with_cryptocurrency import spaceAmount


@dp.callback_query_handler(text="continueCreateAdvert", state='*')
async def continueCreateAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    if data.get('limitHigh'):
        category = await database.get_category(data.get('category_id'))
        subcategory = await database.get_subcategory(data.get('subcategory_id'))
        course = await database.get_course(data.get('cryptocurrency'))
        my_course_text = ""
        if data.get('fixPrice'):
            if data['currency'] == "USD":
                my_course_text = f'${data["fixPrice"]}'
            elif data['currency'] == "RUB":
                my_course_text = f'{data["fixPrice"]} ₽'
        else:
            my_percent = 100 + data['percent'] if data['decimalPercent'] == "+" else 100 - data['percent']
            if data['currency'] == "USD":
                my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({data["decimalPercent"]}{data["percent"]}%)'
            elif data['currency'] == "RUB":
                my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({data["decimalPercent"]}{data["percent"]}%)'

        buy_or_sell_text = "покупатель" if data['is_sell'] == True else "продавец"
        key = await create_advert_comment_keyboard()
        await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                     f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                     f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                     f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n"
                                     f"<b>∙ Лимиты на отклик:</b> {data['limitLow']}-{data['limitHigh']} {data['cryptocurrency']}\n\n"
                                     f"👉 Введите комментарий, который будет видеть {buy_or_sell_text} перед началом сделки, или оставьте объявление без комментария:",
                                     reply_markup=key, disable_web_page_preview=True)
        await CreateAdvertStatesGroup.set_comment.set()
    elif data.get('fixPrice') or data.get('percent'):
        category = await database.get_category(data.get('category_id'))
        subcategory = await database.get_subcategory(data.get('subcategory_id'))
        course = await database.get_course(data['cryptocurrency'])
        my_course_text = ""
        if data.get('fixPrice'):
            if data['currency'] == "USD":
                my_course_text = f'${data["fixPrice"]}'
            elif data['currency'] == "RUB":
                my_course_text = f'{data["fixPrice"]} ₽'
        else:
            my_percent = 100 + data['percent'] if data['decimalPercent'] == "+" else 100 - data['percent']
            if data['currency'] == "USD":
                my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({data["decimalPercent"]}{data["percent"]}%)'
            elif data['currency'] == "RUB":
                my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({data["decimalPercent"]}{data["percent"]}%)'
        key = await create_advert_limit_keyboard(data['subcategory_id'])
        await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                     f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                     f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                     f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n\n"
                                     f"👉 Введите лимиты на отклик в {data['cryptocurrency']} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                     reply_markup=key, disable_web_page_preview=True)
        await CreateAdvertStatesGroup.set_limit.set()
    elif data.get('subcategory_id'):
        category = await database.get_category(data.get('category_id'))
        subcategory = await database.get_subcategory(data.get('subcategory_id'))
        course = await database.get_course(data['cryptocurrency'])
        course_text = ""
        language_mode = ""
        if data['currency'] == "USD":
            course_text = f'${await spaceAmount(course.course)}'
        elif data['currency'] == "RUB":
            course_text = f'{await spaceAmount(course.course_rub)} ₽'
            language_mode = "ru/"
        await state.update_data(language_mode=language_mode)
        key = await create_advert_price_keyboard(data['category_id'])
        if data['cryptocurrency'].lower() == 'ton':
            crypto_for_site = 'toncoin'
        else:
            crypto_for_site = data['cryptocurrency'].lower()
        await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                     f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                     f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n\n"
                                     f"<a href='https://coinmarketcap.com/{language_mode}currencies/{crypto_for_site}/'>Курс {data['cryptocurrency']}</a>: {course_text}\n\n"
                                     f"👉 Введите свой курс для объявления в виде фиксированного числа или разницы в процентах от курса:\n\n"
                                     f"❗ Число можно указать дробное через точку. (3.7) Процент обязательно со знаком. (+3.5 или -6)",
                                     reply_markup=key, disable_web_page_preview=True)
        await CreateAdvertStatesGroup.enter_price.set()
    elif data.get('category_id'):
        category = await database.get_category(data['category_id'])
        key = await create_advert_subcategory_keyboard(data['currency'], data['category_id'])
        await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                     f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b> ({category.name})\n\n"
                                     f"👉 Выберите удобный для себя способ {data['select_payment_text']} денег:",
                                     reply_markup=key)
    elif data.get('currency'):
        key = await create_advert_category_keyboard(data['cryptocurrency'], data['currency'])
        await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                     f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                     f"👉 Выберите категорию, в которой хотите разместить объявление:",
                                     reply_markup=key)
    elif data.get('cryptocurrency'):
        key = await create_advert_currency_keyboard(data['is_sell_original'])
        await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                     f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b>\n\n"
                                     f"👉 Выберите валюту для проведения обмена:",
                                     reply_markup=key)
    else:
        key = await create_advert_cryptocurrency_keyboard()
        await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                     f"<b>{data['is_sell_text']}</b>\n\n"
                                     f"👉 Выберите какую криптовалюту хотите {data['is_sell_text'].lower()}:",
                                     reply_markup=key)
