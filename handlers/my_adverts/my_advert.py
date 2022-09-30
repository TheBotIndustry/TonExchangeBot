from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.exchange import my_adverts_keyboard
from keyboards.my_advert import my_advert_keyboard, my_advert_course_limit_keyboard, my_advert_course_comment_keyboard, \
    my_advert_delete_keyboard
from loader import dp, database
from utils.other.operations_with_cryptocurrency import spaceAmount


class EditMyAdvertStatesGroup(StatesGroup):
    set_course = State()
    set_limit = State()
    set_comment = State()


@dp.callback_query_handler(text_startswith='myAdvert_', state='*')
async def myAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    advert = await database.get_advert(advert_id)
    data = await state.get_data()
    key = await my_advert_keyboard(advert_id, data)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    course = await database.get_course(advert.cryptocurrency)
    my_course_text = ""
    if advert.fixPrice:
        if advert.currency == "USD":
            my_course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            my_course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({advert.decimalPercent}{advert.percent}%)'
        elif advert.currency == "RUB":
            my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({advert.decimalPercent}{advert.percent}%)'
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    status_text = "✅" if advert.status else "🚫"
    await call.message.edit_text(f"<b>{status_text} Ваше объявление:</b>\n\n"
                                 f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                 f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                 f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
                                 f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                                 f"{comment_text}", reply_markup=key)


@dp.callback_query_handler(text_startswith='myAdvertChangeCourse_', state='*')
async def myAdvertChangeCourse_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    await state.update_data(my_advert_id=advert_id)
    advert = await database.get_advert(advert_id)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    course = await database.get_course(advert.cryptocurrency)
    my_course_text = ""
    if advert.fixPrice:
        if advert.currency == "USD":
            my_course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            my_course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({advert.decimalPercent}{advert.percent}%)'
        elif advert.currency == "RUB":
            my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({advert.decimalPercent}{advert.percent}%)'
    course_text = ""
    language_mode = ""
    if advert.currency == "USD":
        course_text = f'${await spaceAmount(course.course)}'
    elif advert.currency == "RUB":
        course_text = f'{await spaceAmount(course.course_rub)} ₽'
        language_mode = "ru/"
    currencySourse = advert.cryptocurrency.lower()
    if currencySourse == "ton":
        currencySourse = "toncoin"
    key = await my_advert_course_limit_keyboard(advert_id)
    await call.message.edit_text(f"<b>✏ Ваше объявление:</b>\n\n"
                                 f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                 f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                 f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
                                 f"<b>∙ </b><a href='https://coinmarketcap.com/{language_mode}currencies/{currencySourse}/'>Курс {advert.cryptocurrency}:</a> {course_text}\n\n"
                                 f"👉 Введите свой курс для объявления в виде фиксированного числа или разницы в процентах от курса:\n\n"
                                 f"❗ Число можно указать дробное через точку. (3.7) Процент обязательно со знаком. (+3.5 или -6)",
                                 reply_markup=key, disable_web_page_preview=True)
    await EditMyAdvertStatesGroup.set_course.set()


@dp.message_handler(state=EditMyAdvertStatesGroup.set_course)
async def editMyAdvertState_set_course(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    try:
        await dp.bot.delete_message(message.chat.id, data['second_message'])
    except:
        pass
    await message.delete()
    advert_id = data['my_advert_id']
    advert = await database.get_advert(advert_id)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    course = await database.get_course(advert.cryptocurrency)
    my_course_text = ""
    if advert.fixPrice:
        if advert.currency == "USD":
            my_course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            my_course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({advert.decimalPercent}{advert.percent}%)'
        elif advert.currency == "RUB":
            my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({advert.decimalPercent}{advert.percent}%)'
    course_text = ""
    language_mode = ""
    if advert.currency == "USD":
        course_text = f'${await spaceAmount(course.course)}'
    elif advert.currency == "RUB":
        course_text = f'{await spaceAmount(course.course_rub)} ₽'
        language_mode = "ru/"
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""

    if message.text[0] == "+" or message.text[0] == "-":
        try:
            percent = float(message.text[1:])
            decimalPercent = message.text[0]
            await database.edit_my_advert_course(
                advert_id=advert_id,
                percent=percent,
                decimalPercent=decimalPercent
            )
            my_percent = 100 + percent if decimalPercent == "+" else 100 - percent
            my_course_text = ""
            if advert.currency == "USD":
                my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({decimalPercent}{percent}%)'
            elif advert.currency == "RUB":
                my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({decimalPercent}{percent}%)'
            data = await state.get_data()
            key = await my_advert_keyboard(advert_id, data)
            status_text = "✅" if advert.status else "🚫"
            second_message = await message.answer(
                f"<b>Курс изменён.</b>\n\n"
                f"<b>{status_text} Ваше объявление:</b>\n\n"
                f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
                f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                f"{comment_text}",
                reply_markup=key)
            await state.update_data(second_message=second_message.message_id)
        except:
            currencySourse = advert.cryptocurrency.lower()
            if currencySourse == "ton":
                currencySourse = "toncoin"
            key = await my_advert_course_limit_keyboard(advert_id)
            second_message = await message.answer(f"<b>Ошибка ввода</b>\n\n"
                                                  f"<b>✏ Ваше объявление:</b>\n\n"
                                                  f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                                  f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                                  f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
                                                  f"<b>∙ </b><a href='https://coinmarketcap.com/{language_mode}currencies/{currencySourse}/'>Курс {advert.cryptocurrency}:</a> {course_text}\n\n"
                                                  f"👉 Введите свой курс для объявления в виде фиксированного числа или разницы в процентах от курса:\n\n"
                                                  f"❗ Число можно указать дробное через точку. (3.7) Процент обязательно со знаком. (+3.5 или -6)",
                                                  reply_markup=key, disable_web_page_preview=True)
            await state.update_data(second_message=second_message.message_id)
            await EditMyAdvertStatesGroup.set_course.set()
    else:
        try:
            fixPrice = float(message.text)
            await database.edit_my_advert_course(
                advert_id=advert_id,
                fixPrice=fixPrice
            )
            my_course_text = ""
            if advert.currency == "USD":
                my_course_text = f'${fixPrice}'
            elif advert.currency == "RUB":
                my_course_text = f'{fixPrice} ₽'
            data = await state.get_data()
            key = await my_advert_keyboard(advert_id, data)
            status_text = "✅" if advert.status else "🚫"
            second_message = await message.answer(
                f"<b>Курс изменён.</b>\n\n"
                f"<b>{status_text} Ваше объявление:</b>\n\n"
                f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
                f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                f"{comment_text}",
                reply_markup=key)
            await state.update_data(second_message=second_message.message_id)
        except:
            currencySourse = advert.cryptocurrency.lower()
            if currencySourse == "ton":
                currencySourse = "toncoin"
            key = await my_advert_course_limit_keyboard(advert_id)
            second_message = await message.answer(f"<b>Ошибка ввода</b>\n\n"
                                                  f"<b>✏ Ваше объявление:</b>\n\n"
                                                  f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                                  f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                                  f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
                                                  f"<b>∙ </b><a href='https://coinmarketcap.com/{language_mode}currencies/{currencySourse}/'>Курс {advert.cryptocurrency}:</a> {course_text}\n\n"
                                                  f"👉 Введите свой курс для объявления в виде фиксированного числа или разницы в процентах от курса:\n\n"
                                                  f"❗ Число можно указать дробное через точку. (3.7) Процент обязательно со знаком. (+3.5 или -6)",
                                                  reply_markup=key, disable_web_page_preview=True)
            await state.update_data(second_message=second_message.message_id)
            await EditMyAdvertStatesGroup.set_course.set()


@dp.callback_query_handler(text_startswith='myAdvertChangeLimit_', state='*')
async def myAdvertChangeLimit_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    await state.update_data(my_advert_id=advert_id)
    advert = await database.get_advert(advert_id)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    key = await my_advert_course_limit_keyboard(advert_id)
    await call.message.edit_text(f"<b>✏ Ваше объявление:</b>\n\n"
                                 f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                 f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                 f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}\n\n"
                                 f"👉 Введите лимиты на отклик в {advert.cryptocurrency} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                 reply_markup=key)
    await EditMyAdvertStatesGroup.set_limit.set()


@dp.message_handler(state=EditMyAdvertStatesGroup.set_limit)
async def editMyAdvertState_set_limit(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    try:
        await dp.bot.delete_message(message.chat.id, data['second_message'])
    except:
        pass
    await message.delete()
    advert_id = data['my_advert_id']
    advert = await database.get_advert(advert_id)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    limit_split = message.text.split("-")
    try:
        if len(limit_split) == 2:
            limitLow = float(limit_split[0])
            limitHigh = float(limit_split[1])
            if limitHigh > limitLow > 0:
                await database.edit_my_advert_limit(
                    advert_id=advert_id,
                    limitLow=limitLow,
                    limitHigh=limitHigh
                )
                advert = await database.get_advert(advert_id)
                course = await database.get_course(advert.cryptocurrency)
                my_course_text = ""
                if advert.fixPrice:
                    if advert.currency == "USD":
                        my_course_text = f'${advert.fixPrice}'
                    elif advert.currency == "RUB":
                        my_course_text = f'{advert.fixPrice} ₽'
                else:
                    my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
                    if advert.currency == "USD":
                        my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({advert.decimalPercent}{advert.percent}%)'
                    elif advert.currency == "RUB":
                        my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({advert.decimalPercent}{advert.percent}%)'
                comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
                data = await state.get_data()
                key = await my_advert_keyboard(advert_id, data)
                status_text = "✅" if advert.status else "🚫"
                second_message = await message.answer(
                    f"<b>Лимиты изменены.</b>\n\n"
                    f"<b>{status_text} Ваше объявление:</b>\n\n"
                    f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                    f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                    f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
                    f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                    f"{comment_text}",
                    reply_markup=key)
                await state.update_data(second_message=second_message.message_id)
            else:
                key = await my_advert_course_limit_keyboard(advert_id)
                second_message = await message.answer(f"<b>Ошибка ввода</b>\n\n"
                                                      f"<b>✏ Ваше объявление:</b>\n\n"
                                                      f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                                      f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                                      f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}\n\n"
                                                      f"👉 Введите лимиты на отклик в {advert.cryptocurrency} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                                      reply_markup=key)
                await state.update_data(second_message=second_message.message_id)
                await EditMyAdvertStatesGroup.set_limit.set()
        else:
            key = await my_advert_course_limit_keyboard(advert_id)
            second_message = await message.answer(f"<b>Ошибка ввода</b>\n\n"
                                                  f"<b>✏ Ваше объявление:</b>\n\n"
                                                  f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                                  f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                                  f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}\n\n"
                                                  f"👉 Введите лимиты на отклик в {advert.cryptocurrency} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                                  reply_markup=key)
            await state.update_data(second_message=second_message.message_id)
            await EditMyAdvertStatesGroup.set_limit.set()
    except:
        key = await my_advert_course_limit_keyboard(advert_id)
        second_message = await message.answer(f"<b>Ошибка ввода</b>\n\n"
                                              f"<b>✏ Ваше объявление:</b>\n\n"
                                              f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                              f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                              f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}\n\n"
                                              f"👉 Введите лимиты на отклик в {advert.cryptocurrency} (минимальная и максимальная сумма сделки через дефис. Например: 10-100):",
                                              reply_markup=key)
        await state.update_data(second_message=second_message.message_id)
        await EditMyAdvertStatesGroup.set_limit.set()


@dp.callback_query_handler(text_startswith='myAdvertChangeComment_', state='*')
async def myAdvertChangeComment_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    await state.update_data(my_advert_id=advert_id)
    advert = await database.get_advert(advert_id)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    buy_or_sell_text = "покупатель" if advert.is_sell == True else "продавец"
    key = await my_advert_course_comment_keyboard(advert_id)
    await call.message.edit_text(f"<b>✏ Ваше объявление:</b>\n\n"
                                 f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                 f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})"
                                 f"{comment_text}\n\n"
                                 f"👉 Введите комментарий, который будет видеть {buy_or_sell_text} перед началом сделки, или оставьте объявление без комментария:",
                                 reply_markup=key)
    await EditMyAdvertStatesGroup.set_comment.set()


@dp.message_handler(state=EditMyAdvertStatesGroup.set_comment)
async def editMyAdvertState_set_comment(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    try:
        await dp.bot.delete_message(message.chat.id, data['second_message'])
    except:
        pass
    await message.delete()
    advert_id = data['my_advert_id']
    await database.edit_my_advert_comment(advert_id=advert_id, comment=message.text)
    advert = await database.get_advert(advert_id)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    advert = await database.get_advert(advert_id)
    course = await database.get_course(advert.cryptocurrency)
    my_course_text = ""
    if advert.fixPrice:
        if advert.currency == "USD":
            my_course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            my_course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({advert.decimalPercent}{advert.percent}%)'
        elif advert.currency == "RUB":
            my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({advert.decimalPercent}{advert.percent}%)'
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    data = await state.get_data()
    key = await my_advert_keyboard(advert_id, data)
    status_text = "✅" if advert.status else "🚫"
    second_message = await message.answer(
        f"<b>Комментарий изменён.</b>\n\n"
        f"<b>{status_text} Ваше объявление:</b>\n\n"
        f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
        f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
        f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
        f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
        f"{comment_text}",
        reply_markup=key)
    await state.update_data(second_message=second_message.message_id)


@dp.callback_query_handler(text_startswith='myAdvertDeleteComment_', state='*')
async def myAdvertDeleteComment_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    await database.edit_my_advert_comment(advert_id=advert_id, comment=None)
    advert = await database.get_advert(advert_id)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    advert = await database.get_advert(advert_id)
    course = await database.get_course(advert.cryptocurrency)
    my_course_text = ""
    if advert.fixPrice:
        if advert.currency == "USD":
            my_course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            my_course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({advert.decimalPercent}{advert.percent}%)'
        elif advert.currency == "RUB":
            my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({advert.decimalPercent}{advert.percent}%)'
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    data = await state.get_data()
    key = await my_advert_keyboard(advert_id, data)
    status_text = "✅" if advert.status else "🚫"
    await call.message.edit_text(
        f"<b>Комментарий удалён.</b>\n\n"
        f"<b>{status_text} Ваше объявление:</b>\n\n"
        f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
        f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
        f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
        f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
        f"{comment_text}",
        reply_markup=key)


@dp.callback_query_handler(text_startswith='myAdvertDelete_', state='*')
async def myAdvertDelete_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    key = await my_advert_delete_keyboard(advert_id)
    await call.message.edit_text("Вы уверены, что хотите удалить это объявление?",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='myAdvertAcceptDelete_', state='*')
async def myAdvertAcceptDelete_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    await database.delete_advert(advert_id)
    data = await state.get_data()
    adverts = await database.get_adverts_user(call.message.chat.id, data.get('filterMyAdvert'))
    key = await my_adverts_keyboard(adverts, data)
    if not adverts:
        await call.message.edit_text("<b>Объявление удалено.</b>\n\n"
                                     "<b>🗒 Ваше объявления</b>\n\n"
                                     "У Вас ещё нет объявлений.\n\n"
                                     "👌 Можно их создать.",
                                     reply_markup=key)
    else:
        await call.message.edit_text(f"<b>Объявление удалено.</b>\n\n"
                                     f"<b>🗒 Ваше объявления</b>\n\n"
                                     f"Список Ваших объявлений:",
                                     reply_markup=key)


@dp.callback_query_handler(text_startswith='myAdvertChangeStatus_', state='*')
async def myAdvertChangeStatus_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[1]
    advert = await database.get_advert(advert_id)
    advert_old_status = advert.status
    await database.advert_change_status(advert_id)
    advert = await database.get_advert(advert_id)
    if advert.status:
        await call.answer("✅ Объявление включено", show_alert=True)
    else:
        if advert_old_status:
            await call.answer("🚫 Объявление выключено", show_alert=True)
        else:
            await call.answer(
                f"⚠  Для включения объявления необходимо иметь на счету {advert.limitHigh} {advert.cryptocurrency}",
                show_alert=True)
    data = await state.get_data()
    key = await my_advert_keyboard(advert_id, data)
    is_sell_text = "Продаю" if advert.is_sell else "Покупаю"
    select_payment_text = "приёма" if advert.is_sell else "отправки"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    course = await database.get_course(advert.cryptocurrency)
    my_course_text = ""
    if advert.fixPrice:
        if advert.currency == "USD":
            my_course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            my_course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            my_course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))} ({advert.decimalPercent}{advert.percent}%)'
        elif advert.currency == "RUB":
            my_course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽ ({advert.decimalPercent}{advert.percent}%)'
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    status_text = "✅" if advert.status else "🚫"
    await call.message.edit_text(f"<b>{status_text} Ваше объявление:</b>\n\n"
                                 f"<b>{is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                                 f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                                 f"<b>∙ Ваш курс {advert.cryptocurrency}:</b> {my_course_text}\n"
                                 f"<b>∙ Лимиты на отклик:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                                 f"{comment_text}", reply_markup=key)
