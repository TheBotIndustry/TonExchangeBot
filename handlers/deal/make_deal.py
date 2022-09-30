from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from handlers.deal.sendPayments import SendPayments_StatesGroup
from keyboards.deal import deal_back_keyboard, deal_start_keyboard, deal_adverts_keyboard, accept_make_deal_keyboard, \
    createDealCreator_keyboard, createDealContrAgent_keyboard, send_payment_deal_keyboard
from keyboards.exchange import exchange_keyboard
from keyboards.start import starting_keyboard
from loader import dp, database
from utils.other.messages import delete_first_second_messages
from utils.other.operations_with_cryptocurrency import spaceAmount


class DealStatesGroup(StatesGroup):
    enter_amount = State()


@dp.callback_query_handler(text_startswith='makeDeal_', state='*')
async def makeDeal_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    advert_id = call.data.split("_")[-1]
    await state.update_data(deal_advert_id=advert_id)
    advert = await database.get_advert(advert_id)
    deal_is_sell = True if not advert.is_sell else False
    await state.update_data(deal_is_sell=deal_is_sell)
    await state.update_data(deal_select_value=advert.cryptocurrency)
    main_deal_is_sell_text = "Продажа" if deal_is_sell else "Покупка"
    deal_is_sell_text = "продать" if deal_is_sell else "купить"
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
    data = await state.get_data()
    if deal_is_sell:
        limitLow = 0
        limitHigh = 0
        balance = await database.get_balance_user(call.message.chat.id, advert.cryptocurrency)
        if balance >= advert.limitLow:
            if balance >= advert.limitHigh:
                limitLow, limitHigh = advert.limitLow, advert.limitHigh
            else:
                limitLow, limitHigh = advert.limitLow, balance
        if limitLow == 0:
            await call.answer("У Вас недостаточно средств на счету для сделки", show_alert=True)
            return
    else:
        limitLow, limitHigh = advert.limitLow, advert.limitHigh
    await delete_first_second_messages(call.message.chat.id, data)
    key = await deal_back_keyboard(advert.currency)
    first_message = await call.message.answer("💸", reply_markup=key)
    second_message = await call.message.answer(
        f"<b>{main_deal_is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
        f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
        f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}"
        f"{comment_text}\n\n"
        f"👉 Введите в <b>{advert.cryptocurrency}</b> (от {limitLow} до {limitHigh}) сколько хотите {deal_is_sell_text}:")
    await state.update_data(first_message=first_message.message_id, second_message=second_message.message_id)
    await DealStatesGroup.enter_amount.set()


@dp.message_handler(text='⬅ Назад', state='*')
async def back_deal_handler(message: types.Message, state: FSMContext):
    await message.delete()
    await state.reset_state(False)
    data = await state.get_data()
    advert_id = data['deal_advert_id']
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
    await delete_first_second_messages(message.chat.id, data)
    key = await starting_keyboard()
    first_message = await message.answer("💸", reply_markup=key)
    key = await deal_start_keyboard(advert_id, subcategory.id)
    second_message = await message.answer(
        f"Вы можете <b>{buy_or_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
        f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
        f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}\n"
        f"<b>∙ Мин-макс сумма сделки:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
        f"{comment_text}", reply_markup=key)
    await state.update_data(first_message=first_message.message_id,
                            second_message=second_message.message_id)


@dp.message_handler(text_startswith='Ввести в ', state='*')
async def enter_in_deal_handler(message: types.Message, state: FSMContext):
    await message.delete()
    await state.reset_state(False)
    data = await state.get_data()
    advert_id = data['deal_advert_id']
    advert = await database.get_advert(advert_id)
    deal_select_value = message.text.split("Ввести в ")[-1]
    await state.update_data(deal_select_value=deal_select_value)
    deal_next_value = advert.currency if deal_select_value == advert.cryptocurrency else advert.cryptocurrency
    deal_is_sell = True if not advert.is_sell else False
    await state.update_data(deal_is_sell=deal_is_sell)
    main_deal_is_sell_text = "Продажа" if deal_is_sell else "Покупка"
    deal_is_sell_text = "продать" if deal_is_sell else "купить"
    select_payment_text = "отправки" if advert.is_sell == True else "получения"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    course = await database.get_course(advert.cryptocurrency)
    course_text = ""
    course_real = 1
    if advert.fixPrice:
        course_real = advert.fixPrice
        if advert.currency == "USD":
            course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            course_real = round(course.course / 100 * my_percent, 2)
            course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))}'
        elif advert.currency == "RUB":
            course_real = round(course.course_rub / 100 * my_percent, 2)
            course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽'
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    data = await state.get_data()
    if deal_is_sell:
        limitLow = 0
        limitHigh = 0
        balance = await database.get_balance_user(message.chat.id, advert.cryptocurrency)
        if balance >= advert.limitLow:
            if balance >= advert.limitHigh:
                limitLow, limitHigh = advert.limitLow, advert.limitHigh
            else:
                limitLow, limitHigh = advert.limitLow, balance
    else:
        limitLow, limitHigh = advert.limitLow, advert.limitHigh
    await delete_first_second_messages(message.chat.id, data)
    if limitLow == 0:
        key = await starting_keyboard()
        first_message = await message.answer("💸", reply_markup=key)
        key = await deal_start_keyboard(advert_id, subcategory.id)
        buy_or_sell_text = "купить" if advert.is_sell == True else "продать"
        second_message = await message.answer(
            f"<b>У Вас недостаточно средств для начала сделки</b>\n\n"
            f"Вы можете <b>{buy_or_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
            f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
            f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}\n"
            f"<b>∙ Мин-макс сумма сделки:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
            f"{comment_text}", reply_markup=key)
        await state.update_data(first_message=first_message.message_id,
                                second_message=second_message.message_id)
        return
    key = await deal_back_keyboard(deal_next_value)
    first_message = await message.answer("💸", reply_markup=key)
    limitText = f"от {limitLow} до {limitHigh}" if deal_select_value == advert.cryptocurrency else \
        f"от {round(limitLow * course_real, 2)} до {round(limitHigh * course_real, 2)}"
    second_message = await message.answer(
        f"<b>{main_deal_is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
        f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
        f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}"
        f"{comment_text}\n\n"
        f"👉 Введите в <b>{deal_select_value}</b> ({limitText}) сколько хотите {deal_is_sell_text}:")
    await state.update_data(first_message=first_message.message_id, second_message=second_message.message_id)
    await DealStatesGroup.enter_amount.set()


@dp.message_handler(state=DealStatesGroup.enter_amount)
async def DealStatesGroup_enter_amount_state(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    await message.delete()
    try:
        await dp.bot.delete_message(message.chat.id, data['second_message'])
    except:
        pass
    deal_is_sell = data['deal_is_sell']
    deal_advert_id = data['deal_advert_id']
    advert = await database.get_advert(deal_advert_id)
    main_deal_is_sell_text = "Продажа" if deal_is_sell else "Покупка"
    deal_is_sell_text = "продать" if deal_is_sell else "купить"
    select_payment_text = "отправки" if advert.is_sell == True else "получения"
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    course = await database.get_course(advert.cryptocurrency)
    course_text = ""
    course_real = 1
    if advert.fixPrice:
        course_real = advert.fixPrice
        if advert.currency == "USD":
            course_text = f'${advert.fixPrice}'
        elif advert.currency == "RUB":
            course_text = f'{advert.fixPrice} ₽'
    else:
        my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
        if advert.currency == "USD":
            course_real = round(course.course / 100 * my_percent, 2)
            course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))}'
        elif advert.currency == "RUB":
            course_real = round(course.course_rub / 100 * my_percent, 2)
            course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽'
    comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
    deal_select_value = data['deal_select_value']
    if deal_is_sell:
        limitLowUser = 0
        limitHighUser = 0
        balance = await database.get_balance_user(message.chat.id, advert.cryptocurrency)
        if balance >= advert.limitLow:
            if balance >= advert.limitHigh:
                limitLowUser, limitHighUser = advert.limitLow, advert.limitHigh
            else:
                limitLowUser, limitHighUser = advert.limitLow, balance
    else:
        limitLowUser, limitHighUser = advert.limitLow, advert.limitHigh
    limitText = f"от {limitLowUser} до {limitHighUser}" if deal_select_value == advert.cryptocurrency else \
        f"от {round(limitLowUser * course_real, 2)} до {round(limitHighUser * course_real, 2)}"
    if limitLowUser == 0:
        await delete_first_second_messages(message.chat.id, data)
        key = await starting_keyboard()
        first_message = await message.answer("💸", reply_markup=key)
        key = await deal_start_keyboard(deal_advert_id, subcategory.id)
        buy_or_sell_text = "купить" if advert.is_sell == True else "продать"
        second_message = await message.answer(
            f"<b>У Вас недостаточно средств для начала сделки</b>\n\n"
            f"Вы можете <b>{buy_or_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
            f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
            f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}\n"
            f"<b>∙ Мин-макс сумма сделки:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
            f"{comment_text}", reply_markup=key)
        await state.update_data(first_message=first_message.message_id,
                                second_message=second_message.message_id)
        return
    try:
        amount = float(message.text)
        limitHigh = limitHighUser if deal_select_value == advert.cryptocurrency else round(
            limitHighUser * course_real, 2)
        limitLow = limitLowUser if deal_select_value == advert.cryptocurrency else round(
            limitLowUser * course_real, 2)
        if limitHigh >= amount >= limitLow:
            advert = await database.get_advert(deal_advert_id)
            if advert is not None and advert.status:
                if deal_select_value == advert.cryptocurrency:
                    amount_crypto = amount
                else:
                    if advert.cryptocurrency == "TON":
                        amount_crypto = round(amount / course_real, 2)
                    else:
                        amount_crypto = round(amount / course_real, 8)
                amount_currency = round(amount_crypto * course_real, 2)
                await state.update_data(amount_crypto=amount_crypto, amount_currency=amount_currency)
                await delete_first_second_messages(message.chat.id, data)
                key = await starting_keyboard()
                first_message = await message.answer("💸", reply_markup=key)
                key = await accept_make_deal_keyboard(advert.id)
                market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
                buy_or_sell_smile = "⤴️" if deal_is_sell else "⤵️"
                comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
                second_message = await message.answer(
                    f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                    f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                    f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}"
                    f"{comment_text}\n\n"
                    f"{buy_or_sell_smile} Вы уверены, что хотите {deal_is_sell_text} <b>{amount_crypto} {advert.cryptocurrency}</b> за <b>{amount_currency} {advert.currency}</b>?",
                    reply_markup=key)
                await state.update_data(first_message=first_message.message_id,
                                        second_message=second_message.message_id)
            else:
                await delete_first_second_messages(message.chat.id, data)
                key = await starting_keyboard()
                first_message = await message.answer("💸", reply_markup=key)
                adverts = await database.get_adverts_market(market_is_sell=data['market_is_sell'],
                                                            currency=data['market_currency'],
                                                            subcategory_id=data['market_subcategory_id'],
                                                            cryptocurrency=data['market_cryptocurrency'])
                key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                                  message.chat.id, data['filterAdvertAmount'], 1)
                market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
                second_message = await message.answer(
                    f"<b>Объявление в данный момент недоступно.</b>\n\n"
                    f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                    f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                    f"👉 Выберите подходящее объявление:\n\n"
                    f"<i>Ваши объявления со знаком «🔷».</i>",
                    reply_markup=key)
                await state.update_data(first_message=first_message.message_id,
                                        second_message=second_message.message_id)
        else:
            second_message = await message.answer(
                f"<b>Ошибка ввода</b>\n\n"
                f"<b>{main_deal_is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}"
                f"{comment_text}\n\n"
                f"👉 Введите в <b>{deal_select_value}</b> ({limitText}) сколько хотите {deal_is_sell_text}:")
            await state.update_data(second_message=second_message.message_id)
            await DealStatesGroup.enter_amount.set()
    except Exception as error:
        print(error)
        second_message = await message.answer(
            f"<b>Ошибка ввода</b>\n\n"
            f"<b>{main_deal_is_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
            f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
            f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}"
            f"{comment_text}\n\n"
            f"👉 Введите в <b>{deal_select_value}</b> ({limitText}) сколько хотите {deal_is_sell_text}:")
        await state.update_data(second_message=second_message.message_id)
        await DealStatesGroup.enter_amount.set()


@dp.callback_query_handler(text='areYouSure?', state='*')
async def areYouSure_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    advert = await database.get_advert(data['deal_advert_id'])
    category = await database.get_category(advert.category_id)
    subcategory = await database.get_subcategory(advert.subCategory_id)
    if advert is not None and advert.status:
        course = await database.get_course(advert.cryptocurrency)
        course_text = ""
        course_real = 1
        if advert.fixPrice:
            course_real = advert.fixPrice
            if advert.currency == "USD":
                course_text = f'${advert.fixPrice}'
            elif advert.currency == "RUB":
                course_text = f'{advert.fixPrice} ₽'
        else:
            my_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
            if advert.currency == "USD":
                course_real = round(course.course / 100 * my_percent, 2)
                course_text = f'${await spaceAmount(round(course.course / 100 * my_percent, 2))}'
            elif advert.currency == "RUB":
                course_real = round(course.course_rub / 100 * my_percent, 2)
                course_text = f'{await spaceAmount(round(course.course_rub / 100 * my_percent, 2))} ₽'
        comment_text = f"\n<b>∙ Комментарий:</b> {advert.comment}" if advert.comment else ""
        deal_select_value = data['deal_select_value']
        amount_crypto = data['amount_crypto']
        amount_currency = data['amount_currency']
        deal_is_sell = data['deal_is_sell']
        deal_is_sell_text = "продать" if deal_is_sell else "купить"
        if deal_select_value == advert.cryptocurrency:
            new_amount_currency = round(amount_crypto * course_real, 2)
            if advert.limitHigh >= amount_crypto >= advert.limitLow:
                if new_amount_currency == amount_currency:
                    deal = await database.add_deal(
                        category_id=advert.category_id, subcategory_id=advert.subCategory_id,
                        advert_id=advert.id, creator_user_id=advert.user_id, user_id=call.message.chat.id,
                        is_sell=deal_is_sell, cryptocurrency=advert.cryptocurrency, currency=advert.currency,
                        amount_crypto=amount_crypto, amount_currency=amount_currency
                    )
                    if not deal.is_sell:
                        try:
                            deal_text = "покупки" if deal.is_sell else "продаже"
                            deal_text_second = "покупаете" if deal.is_sell else "продаёте"
                            market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
                            subcategory = await database.get_subcategory(deal.subcategory_id)
                            category = await database.get_category(deal.category_id)
                            key = await createDealContrAgent_keyboard(deal.id)
                            creator_message = await dp.bot.send_message(deal.creator_user_id,
                                                                        f"📃 У Вас новая сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
                                                                        f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                                        f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                                        f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                                        f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                                                                        f"Вы согласны на данные условия?\n\n"
                                                                        f"<b>⏳ Сделка автоматически закроется, если Вы не ответите в течении 10 минут</b>",
                                                                        reply_markup=key)
                            deal_is_sell_text = "продаёте" if deal_is_sell else "покупаете"
                            market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"

                            data = await state.get_data()
                            await call.message.delete()
                            key = await exchange_keyboard(data)
                            second_message = await call.message.answer(f"<b>🔄 Обмен</b>\n\n"
                                                                       f"💸 Вы можете купить/продать криптовалюту или создать своё объявление.",
                                                                       reply_markup=key)
                            await state.update_data(second_message=second_message.message_id)

                            key = await createDealCreator_keyboard(deal.id)
                            user_message = await call.message.answer(
                                "📃 Создана сделка, ожидайте подтверждения от контрагента.\n\n"
                                f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                f"<b>∙ Условия:</b> Вы <b><u>{deal_is_sell_text}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                                "<b>⏳ Сделка автоматически закроется, если контрагент не ответит в течении 10 минут</b>",
                                reply_markup=key)
                            await database.update_message_deal(deal_id=deal.id, creator_mess_id=creator_message.message_id,
                                                               user_mess_id=user_message.message_id)
                        except:
                            await database.delete_deal(deal.id)
                            adverts = await database.get_adverts_market(market_is_sell=data['market_is_sell'],
                                                                        currency=data['market_currency'],
                                                                        subcategory_id=data['market_subcategory_id'],
                                                                        cryptocurrency=data['market_cryptocurrency'])
                            key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                                              call.message.chat.id, data['filterAdvertAmount'], 1)
                            market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
                            await call.message.edit_text(
                                f"<b>Не удалось связаться с контрагентом, сделка отменена.</b>\n\n"
                                f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                                f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                                f"👉 Выберите подходящее объявление:\n\n"
                                f"<i>Ваши объявления со знаком «🔷».</i>",
                                reply_markup=key)
                    else:
                        key = await send_payment_deal_keyboard(advert.id)
                        await state.update_data(deal_id=deal.id, payment_advert_id=advert.id)
                        await call.message.edit_text(f"👉 Пришлите реквизиты для принятия <b>{deal.currency}</b> на {subcategory.name} ({category.name}):",
                                                     reply_markup=key)
                        await SendPayments_StatesGroup.send_user.set()
                else:
                    await state.update_data(amount_currency=new_amount_currency)
                    key = await accept_make_deal_keyboard(advert.id)
                    market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
                    buy_or_sell_smile = "⤴️" if deal_is_sell else "⤵️"
                    await call.message.edit_text(
                        f"<b>Курс в объявлении изменился.</b>\n\n"
                        f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                        f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                        f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}"
                        f"{comment_text}\n\n"
                        f"{buy_or_sell_smile} Вы уверены, что хотите {deal_is_sell_text} <b>{amount_crypto} {advert.cryptocurrency}</b> за <b>{new_amount_currency} {advert.currency}</b>?",
                        reply_markup=key)
            else:
                buy_or_sell_text = "купить" if advert.is_sell == True else "продать"
                select_payment_text = "отправки" if advert.is_sell == True else "получения"
                key = await deal_start_keyboard(advert.id, subcategory.id)
                await call.message.edit_text(
                    f"<b>Мин-макс сумма сделки изменились.</b>\n\n"
                    f"Вы можете <b>{buy_or_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                    f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                    f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}\n"
                    f"<b>∙ Мин-макс сумма сделки:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                    f"{comment_text}", reply_markup=key)
        else:
            new_amount_crypto = round(amount_currency / course_real, 8)
            if new_amount_crypto == amount_crypto:
                if advert.limitHigh >= amount_crypto >= advert.limitLow:
                    deal = await database.add_deal(
                        category_id=advert.category_id, subcategory_id=advert.subCategory_id,
                        advert_id=advert.id, creator_user_id=advert.user_id, user_id=call.message.chat.id,
                        is_sell=deal_is_sell,
                        cryptocurrency=advert.cryptocurrency, currency=advert.currency,
                        amount_crypto=amount_crypto, amount_currency=amount_currency
                    )
                    try:
                        deal_text = "покупки" if deal.is_sell else "продаже"
                        deal_text_second = "покупаете" if deal.is_sell else "продаёте"
                        market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
                        subcategory = await database.get_subcategory(deal.subcategory_id)
                        category = await database.get_category(deal.category_id)
                        key = await createDealContrAgent_keyboard(deal.id)
                        creator_message = await dp.bot.send_message(deal.creator_user_id,
                                                                    f"📃 У Вас новая сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
                                                                    f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                                    f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                                    f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                                    f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                                                                    f"Вы согласны на данные условия?\n\n"
                                                                    f"<b>⏳ Сделка автоматически закроется, если Вы не ответите в течении 10 минут</b>",
                                                                    reply_markup=key)
                        deal_is_sell_text = "продаёте" if deal_is_sell else "покупаете"
                        market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"

                        await call.message.delete()
                        key = await exchange_keyboard(data)
                        second_message = await call.message.answer(f"<b>🔄 Обмен</b>\n\n"
                                                                   f"💸 Вы можете купить/продать криптовалюту или создать своё объявление.",
                                                                   reply_markup=key)
                        await state.update_data(second_message=second_message.message_id)

                        key = await createDealCreator_keyboard(deal.id)
                        user_message = await call.message.answer(
                            "📃 Создана сделка, ожидайте подтверждения от контрагента.\n\n"
                            f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                            f"<b>∙ Условия:</b> Вы <b><u>{deal_is_sell_text}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                            f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                            "<b>⏳ Сделка автоматически закроется, если контрагент не ответит в течении 10 минут</b>",
                            reply_markup=key)
                        await database.update_message_deal(deal_id=deal.id, creator_mess_id=creator_message.message_id,
                                                           user_mess_id=user_message.message_id)
                    except:
                        await database.delete_deal(deal.id)
                        adverts = await database.get_adverts_market(market_is_sell=data['market_is_sell'],
                                                                    currency=data['market_currency'],
                                                                    subcategory_id=data['market_subcategory_id'],
                                                                    cryptocurrency=data['market_cryptocurrency'])
                        key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                                          call.message.chat.id, data['filterAdvertAmount'], 1)
                        market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
                        await call.message.edit_text(
                            f"<b>Не удалось связаться с контрагентом, сделка отменена.</b>\n\n"
                            f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                            f"👉 Выберите подходящее объявление:\n\n"
                            f"<i>Ваши объявления со знаком «🔷».</i>",
                            reply_markup=key)
                else:
                    buy_or_sell_text = "купить" if advert.is_sell == True else "продать"
                    select_payment_text = "отправки" if advert.is_sell == True else "получения"
                    key = await deal_start_keyboard(advert.id, subcategory.id)
                    await call.message.edit_text(
                        f"<b>Мин-макс сумма сделки изменились.</b>\n\n"
                        f"Вы можете <b>{buy_or_sell_text} {advert.cryptocurrency}</b> за <b>{advert.currency}</b>\n\n"
                        f"<b>∙ Способ {select_payment_text} денег:</b> {subcategory.name} ({category.name})\n"
                        f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}\n"
                        f"<b>∙ Мин-макс сумма сделки:</b> {advert.limitLow}-{advert.limitHigh} {advert.cryptocurrency}"
                        f"{comment_text}", reply_markup=key)
            else:
                await state.update_data(amount_crypto=new_amount_crypto)
                key = await accept_make_deal_keyboard(advert.id)
                market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
                buy_or_sell_smile = "⤴️" if deal_is_sell else "⤵️"
                await call.message.edit_text(
                    f"<b>Курс в объявлении изменился.</b>\n\n"
                    f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                    f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                    f"<b>∙ Курс {advert.cryptocurrency}:</b> {course_text}"
                    f"{comment_text}\n\n"
                    f"{buy_or_sell_smile} Вы уверены, что хотите {deal_is_sell_text} <b>{new_amount_crypto} {advert.cryptocurrency}</b> за <b>{amount_currency} {advert.currency}</b>?",
                    reply_markup=key)
    else:
        adverts = await database.get_adverts_market(market_is_sell=data['market_is_sell'],
                                                    currency=data['market_currency'],
                                                    subcategory_id=data['market_subcategory_id'],
                                                    cryptocurrency=data['market_cryptocurrency'])
        key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                          call.message.chat.id, data['filterAdvertAmount'], 1)
        market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
        await call.message.edit_text(
            f"<b>Объявление в данный момент недоступно.</b>\n\n"
            f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
            f"👉 Выберите подходящее объявление:\n\n"
            f"<i>Ваши объявления со знаком «🔷».</i>",
            reply_markup=key)
