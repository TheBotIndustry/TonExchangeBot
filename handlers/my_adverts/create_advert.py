from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.exchange import create_advert_is_sell_keyboard, create_advert_cryptocurrency_keyboard, \
    create_advert_currency_keyboard, create_advert_category_keyboard, create_advert_subcategory_keyboard, \
    create_advert_price_keyboard, create_advert_limit_keyboard, create_advert_comment_keyboard, \
    create_advert_edit_keyboard
from loader import dp, database
from utils.other.operations_with_cryptocurrency import spaceAmount


class CreateAdvertStatesGroup(StatesGroup):
    enter_price = State()
    set_limit = State()
    set_comment = State()


@dp.callback_query_handler(text='createAdvert', state='*')
async def createAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    key = await create_advert_is_sell_keyboard()
    await state.update_data(is_sell=None, is_sell_text=None, is_sell_original=None, cryptocurrency=None, currency=None, category_id=None, select_payment_text=None,
                            subcategory_id=None,
                            language_mode=None, fixPrice=None, percent=None, decimalPercent=None, my_percent=None,
                            limitLow=None, limitHigh=None)
    await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                 f"👉 Выберите между покупкой и продажей криптовалюты:",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='createAdvertIsSell_', state='*')
async def createAdvertIsSell_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    is_sell = True if call.data.split("_")[1] == "Sell" else False
    is_sell_text = "Продать" if is_sell == True else "Купить"
    await state.update_data(is_sell=is_sell, is_sell_text=is_sell_text, is_sell_original=call.data.split("_")[1])
    key = await create_advert_cryptocurrency_keyboard()
    await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                 f"<b>{is_sell_text}</b>\n\n"
                                 f"👉 Выберите какую криптовалюту хотите {is_sell_text.lower()}:",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='createAdvertCryptocurrency_', state='*')
async def createAdvertCryptocurrency_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    cryptocurrency = call.data.split("_")[1]
    await state.update_data(cryptocurrency=cryptocurrency)
    await state.update_data(currency=None, category_id=None, select_payment_text=None,
                            subcategory_id=None,
                            language_mode=None, fixPrice=None, percent=None, decimalPercent=None, my_percent=None,
                            limitLow=None, limitHigh=None)
    data = await state.get_data()
    key = await create_advert_currency_keyboard(data['is_sell_original'])
    await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                 f"<b>{data['is_sell_text']} {cryptocurrency}</b>\n\n"
                                 f"👉 Выберите валюту для проведения обмена:",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='createAdvertCurrency_', state='*')
async def createAdvertCurrency_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    currency = call.data.split("_")[1]
    await state.update_data(currency=currency)
    await state.update_data(category_id=None, select_payment_text=None,
                            subcategory_id=None,
                            language_mode=None, fixPrice=None, percent=None, decimalPercent=None, my_percent=None,
                            limitLow=None, limitHigh=None)
    data = await state.get_data()
    key = await create_advert_category_keyboard(data['cryptocurrency'], currency)
    await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                 f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{currency}</b>\n\n"
                                 f"👉 Выберите категорию, в которой хотите разместить объявление:",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='createAdvertCategory_', state='*')
async def createAdvertCategory_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    category_id = call.data.split("_")[1]
    data = await state.get_data()
    select_payment_text = "получения" if data['is_sell'] == True else "отправки"
    await state.update_data(category_id=category_id, select_payment_text=select_payment_text)
    await state.update_data(subcategory_id=None,
                            language_mode=None, fixPrice=None, percent=None, decimalPercent=None, my_percent=None,
                            limitLow=None, limitHigh=None)
    category = await database.get_category(category_id)
    key = await create_advert_subcategory_keyboard(data['currency'], category_id)
    await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                 f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b> ({category.name})\n\n"
                                 f"👉 Выберите удобный для себя способ {select_payment_text} денег:",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='createAdvertSubategory_', state='*')
async def createAdvertSubategory_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    subcategory_id = call.data.split("_")[1]
    await state.update_data(subcategory_id=subcategory_id)
    data = await state.get_data()
    category = await database.get_category(data['category_id'])
    subcategory = await database.get_subcategory(subcategory_id)
    course = await database.get_course(data['cryptocurrency'])
    course_text = ""
    language_mode = ""
    if data['currency'] == "USD":
        course_text = f'${await spaceAmount(course.course)}'
    elif data['currency'] == "RUB":
        course_text = f'{await spaceAmount(course.course_rub)} ₽'
        language_mode = "ru/"
    await state.update_data(language_mode=language_mode)
    await state.update_data(fixPrice=None, percent=None, decimalPercent=None, my_percent=None,
                            limitLow=None, limitHigh=None)
    key = await create_advert_price_keyboard(data['category_id'])
    if data['cryptocurrency'].lower() == 'ton':
        crypto_for_site = 'toncoin'
    else:
        crypto_for_site = data['cryptocurrency'].lower()
    await call.message.edit_text(f"<b>➕ Создать объявление</b>\n\n"
                                 f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                 f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n\n"
                                 f"<a href='https://coinmarketcap.com/{language_mode}currencies/{crypto_for_site}'>Курс {data['cryptocurrency']}</a>: {course_text}\n\n"
                                 f"👉 Введите свой курс для объявления в виде фиксированного числа или разницы в процентах от курса:\n\n"
                                 f"❗ Число можно указать дробное через точку. (3.7) Процент обязательно со знаком. (+3.5 или -6)",
                                 reply_markup=key, disable_web_page_preview=True)
    await CreateAdvertStatesGroup.enter_price.set()


@dp.message_handler(state=CreateAdvertStatesGroup.enter_price)
async def createadvertstate_enter_price(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    try:
        await dp.bot.delete_message(message.chat.id, data['second_message'])
    except:
        pass
    await message.delete()
    category = await database.get_category(data['category_id'])
    subcategory = await database.get_subcategory(data['subcategory_id'])
    course = await database.get_course(data['cryptocurrency'])
    course_text = ""
    if data['currency'] == "USD":
        course_text = f'${await spaceAmount(course.course)}'
    elif data['currency'] == "RUB":
        course_text = f'{await spaceAmount(course.course_rub)} ₽'
    if message.text[0] == "+" or message.text[0] == "-":
        try:
            percent = float(message.text[1:])
            decimalPercent = message.text[0]
            my_percent = 100 + percent if decimalPercent == "+" else 100 - percent
            await state.update_data(percent=percent, decimalPercent=decimalPercent, my_percent=my_percent)
            await state.update_data(fixPrice=None, limitLow=None, limitHigh=None)
            my_course_text = ""
            if data['currency'] == "USD":
                my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({decimalPercent}{percent}%)'
            elif data['currency'] == "RUB":
                my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({decimalPercent}{percent}%)'
            key = await create_advert_limit_keyboard(data['subcategory_id'])
            second_message = await message.answer(f"<b>➕ Создать объявление</b>\n\n"
                                                  f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                                  f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                                  f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n\n"
                                                  f"👉 Введите лимиты на отклик в {data['cryptocurrency']} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                                  reply_markup=key, disable_web_page_preview=True)
            await state.update_data(second_message=second_message.message_id)
            await CreateAdvertStatesGroup.set_limit.set()
        except:
            currencySourse = data['cryptocurrency'].lower()
            if currencySourse == "ton":
                currencySourse = "toncoin"
            key = await create_advert_price_keyboard(data['category_id'])
            second_message = await message.answer(f"<b>⚠ Ошибка ввода!</b>\n\n"
                                                  f"<b>➕ Создать объявление</b>\n\n"
                                                  f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                                  f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n\n"
                                                  f"<a href='https://coinmarketcap.com/{data['language_mode']}currencies/{currencySourse}/'>Курс {data['cryptocurrency']}:</a> {course_text}\n\n"
                                                  f"👉 Введите свой курс для объявления в виде фиксированного числа или разницы в процентах от курса:\n\n"
                                                  f"❗ Число можно указать дробное через точку. (3.7) Процент обязательно со знаком. (+3.5 или -6)",
                                                  reply_markup=key, disable_web_page_preview=True)
            await state.update_data(second_message=second_message.message_id)
            await CreateAdvertStatesGroup.enter_price.set()
    else:
        try:
            fixPrice = float(message.text)
            await state.update_data(fixPrice=fixPrice)
            await state.update_data(percent=None, decimalPercent=None, my_percent=None,
                                    limitLow=None, limitHigh=None)
            my_course_text = ""
            if data['currency'] == "USD":
                my_course_text = f'${fixPrice}'
            elif data['currency'] == "RUB":
                my_course_text = f'{fixPrice} ₽'
            key = await create_advert_limit_keyboard(data['subcategory_id'])
            second_message = await message.answer(f"<b>➕ Создать объявление</b>\n\n"
                                                  f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                                  f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                                  f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n\n"
                                                  f"👉 Введите лимиты на отклик в {data['cryptocurrency']} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                                  reply_markup=key, disable_web_page_preview=True)
            await state.update_data(second_message=second_message.message_id)
            await CreateAdvertStatesGroup.set_limit.set()
        except:
            currencySourse = data['cryptocurrency'].lower()
            if currencySourse == "ton":
                currencySourse = "toncoin"
            key = await create_advert_price_keyboard(data['category_id'])
            second_message = await message.answer(f"<b>⚠ Ошибка ввода!</b>\n\n"
                                                  f"<b>➕ Создать объявление</b>\n\n"
                                                  f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                                  f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n\n"
                                                  f"<a href='https://coinmarketcap.com/{data['language_mode']}currencies/{currencySourse}/'>Курс {data['cryptocurrency']}:</a> {data['course_text']}\n\n"
                                                  f"👉 Введите свой курс для объявления в виде фиксированного числа или разницы в процентах от курса:\n\n"
                                                  f"❗ Число можно указать дробное через точку. (3.7) Процент обязательно со знаком. (+3.5 или -6)",
                                                  reply_markup=key, disable_web_page_preview=True)
            await state.update_data(second_message=second_message.message_id)
            await CreateAdvertStatesGroup.enter_price.set()


@dp.message_handler(state=CreateAdvertStatesGroup.set_limit)
async def createadvertstate_enter_price(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    try:
        await dp.bot.delete_message(message.chat.id, data['second_message'])
    except:
        pass
    await message.delete()
    category = await database.get_category(data['category_id'])
    subcategory = await database.get_subcategory(data['subcategory_id'])
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

    try:
        limit_split = message.text.split("-")
        if len(limit_split) == 2:
            limitLow = float(limit_split[0])
            limitHigh = float(limit_split[1])
            if limitHigh > limitLow > 0:
                await state.update_data(limitLow=limitLow, limitHigh=limitHigh)
                buy_or_sell_text = "покупатель" if data['is_sell'] == True else "продавец"
                key = await create_advert_comment_keyboard()
                second_message = await message.answer(f"<b>➕ Создать объявление</b>\n\n"
                                                      f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                                      f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                                      f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n"
                                                      f"<b>∙ Лимиты на отклик:</b> {limitLow}-{limitHigh} {data['cryptocurrency']}\n\n"
                                                      f"👉 Введите комментарий, который будет видеть {buy_or_sell_text} перед началом сделки, или оставьте объявление без комментария:",
                                                      reply_markup=key, disable_web_page_preview=True)
                await state.update_data(second_message=second_message.message_id)
                await CreateAdvertStatesGroup.set_comment.set()
            else:
                key = await create_advert_limit_keyboard(data['subcategory_id'])
                second_message = await message.answer(f"<b>Ошибка ввода</b>\n\n"
                                                      f"<b>➕ Создать объявление</b>\n\n"
                                                      f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                                      f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                                      f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n\n"
                                                      f"👉 Введите лимиты на отклик в {data['cryptocurrency']} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                                      reply_markup=key, disable_web_page_preview=True)
                await state.update_data(second_message=second_message.message_id)
                await CreateAdvertStatesGroup.set_limit.set()
        else:
            key = await create_advert_limit_keyboard(data['subcategory_id'])
            second_message = await message.answer(f"<b>Ошибка ввода</b>\n\n"
                                                  f"<b>➕ Создать объявление</b>\n\n"
                                                  f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                                  f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                                  f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n\n"
                                                  f"👉 Введите лимиты на отклик в {data['cryptocurrency']} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                                  reply_markup=key, disable_web_page_preview=True)
            await state.update_data(second_message=second_message.message_id)
            await CreateAdvertStatesGroup.set_limit.set()
    except:
        key = await create_advert_limit_keyboard(data['subcategory_id'])
        second_message = await message.answer(f"<b>Ошибка ввода</b>\n\n"
                                              f"<b>➕ Создать объявление</b>\n\n"
                                              f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                              f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                              f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n\n"
                                              f"👉 Введите лимиты на отклик в {data['cryptocurrency']} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                              reply_markup=key, disable_web_page_preview=True)
        await state.update_data(second_message=second_message.message_id)
        await CreateAdvertStatesGroup.set_limit.set()


@dp.callback_query_handler(text="createAdvertCourse", state='*')
async def createAdvertCourse_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    category = await database.get_category(data['category_id'])
    subcategory = await database.get_subcategory(data['subcategory_id'])
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


@dp.message_handler(state=CreateAdvertStatesGroup.set_comment)
async def createAdvertStates_set_comment(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    try:
        await dp.bot.delete_message(message.chat.id, data['second_message'])
    except:
        pass
    await message.delete()
    category = await database.get_category(data['category_id'])
    subcategory = await database.get_subcategory(data['subcategory_id'])
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

    advert = await database.add_advert(
        user_id=message.chat.id,
        cryptocurrency=data['cryptocurrency'],
        is_sell=data['is_sell'],
        currency=data['currency'],
        category_id=data['category_id'],
        subCategory_id=data['subcategory_id'],
        limitLow=data['limitLow'],
        limitHigh=data['limitHigh'],
        fixPrice=data.get('fixPrice'),
        percent=data.get('percent'),
        decimalPercent=data.get('decimalPercent'),
        comment=message.text
    )
    await state.update_data(
        create_advert=None,
        cryptocurrency=None,
        is_sell=None,
        is_sell_text=None,
        is_sell_original=None,
        currency=None,
        category_id=None,
        select_payment_text=None,
        subcategory_id=None,
        language_mode=None,
        limitLow=None,
        limitHigh=None,
        fixPrice=None,
        percent=None,
        decimalPercent=None,
        my_percent=None
    )
    key = await create_advert_edit_keyboard(advert.id)
    status_text = "✅ Объявление создано!"
    second_message = await message.answer(f"<b>{status_text}</b>\n\n"
                                          f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                          f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                          f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n"
                                          f"<b>∙ Лимиты на отклик:</b> {data['limitLow']}-{data['limitHigh']} {data['cryptocurrency']}\n"
                                          f"<b>∙ Комментарий:</b> {message.text}",
                                          reply_markup=key)
    await state.update_data(second_message=second_message.message_id)


@dp.callback_query_handler(text='createAdvertWithoutComment', state='*')
async def createAdvertWithoutComment_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    category = await database.get_category(data['category_id'])
    subcategory = await database.get_subcategory(data['subcategory_id'])
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

    advert = await database.add_advert(
        user_id=call.message.chat.id,
        cryptocurrency=data['cryptocurrency'],
        is_sell=data['is_sell'],
        currency=data['currency'],
        category_id=data['category_id'],
        subCategory_id=data['subcategory_id'],
        limitLow=data['limitLow'],
        limitHigh=data['limitHigh'],
        fixPrice=data.get('fixPrice'),
        percent=data.get('percent'),
        decimalPercent=data.get('decimalPercent'),
        comment=None
    )
    await state.update_data(
        create_advert=None,
        cryptocurrency=None,
        is_sell=None,
        is_sell_text=None,
        is_sell_original=None,
        currency=None,
        category_id=None,
        select_payment_text=None,
        subcategory_id=None,
        language_mode=None,
        limitLow=None,
        limitHigh=None,
        fixPrice=None,
        percent=None,
        decimalPercent=None,
        my_percent=None
    )
    status_text = "✅ Объявление создано!"
    key = await create_advert_edit_keyboard(advert.id)
    await call.message.edit_text(f"<b>{status_text}</b>\n\n"
                                 f"<b>{data['is_sell_text']} {data['cryptocurrency']}</b> за <b>{data['currency']}</b>\n\n"
                                 f"<b>∙ Способ {data['select_payment_text']} денег:</b> {subcategory.name} ({category.name})\n"
                                 f"<b>∙ Ваш курс {data['cryptocurrency']}:</b> {my_course_text}\n"
                                 f"<b>∙ Лимиты на отклик:</b> {data['limitLow']}-{data['limitHigh']} {data['cryptocurrency']}",
                                 reply_markup=key)
