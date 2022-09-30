from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.deal import send_payment_deal_keyboard, createDealContrAgent_keyboard, createDealCreator_keyboard, \
    deal_adverts_keyboard, send_payment_creator_deal_keyboard, confirm_send_payment_creator_deal_keyboard, \
    confirm_transfer_user_deal_keyboard
from keyboards.exchange import exchange_keyboard
from loader import dp, database


class SendPayments_StatesGroup(StatesGroup):
    send_user = State()
    send_creator = State()


@dp.message_handler(state=SendPayments_StatesGroup.send_user)
async def sendPayments_send_user_handler(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    await message.delete()
    data = await state.get_data()
    try:
        await dp.bot.delete_message(message.chat.id, data['second_message'])
    except:
        pass
    deal = await database.get_deal(data['deal_id'])
    subcategory = await database.get_subcategory(deal.subcategory_id)
    category = await database.get_category(deal.category_id)
    if len(message.text) <= 200:
        await database.update_payment_deal(deal.id, message.text)
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
            deal_is_sell_text = "продаёте" if deal.is_sell else "покупаете"
            market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"

            data = await state.get_data()
            key = await exchange_keyboard(data)
            second_message = await message.answer(f"<b>🔄 Обмен</b>\n\n"
                                                  f"💸 Вы можете купить/продать криптовалюту или создать своё объявление.",
                                                  reply_markup=key)
            await state.update_data(second_message=second_message.message_id)

            key = await createDealCreator_keyboard(deal.id)
            user_message = await message.answer(
                "📃 Создана сделка, ожидайте подтверждения от контрагента.\n\n"
                f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                f"<b>∙ Условия:</b> Вы <b><u>{deal_is_sell_text}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                f"<b>∙ Реквизиты:</b> <code>{message.text}</code>\n\n"
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
                                              message.chat.id, data['filterAdvertAmount'], 1)
            market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
            second_message = await message.answer(
                f"<b>Не удалось связаться с контрагентом, сделка отменена.</b>\n\n"
                f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                f"👉 Выберите подходящее объявление:\n\n"
                f"<i>Ваши объявления со знаком «🔷».</i>",
                reply_markup=key)
            await state.update_data(second_message=second_message.message_id)
            await database.delete_deal(deal.id)
            if deal.is_sell:
                await database.get_back_deposit(deal.user_id, deal.cryptocurrency, deal.amount_crypto)
    else:
        key = await send_payment_deal_keyboard(data['payment_advert_id'])
        second_message = await message.answer(
            f"<b>Максимум 200 символов</b>\n\n"
            f"👉 Пришлите реквизиты для принятия <b>{deal.currency}</b> на {subcategory.name} ({category.name}):",
            reply_markup=key)
        await state.update_data(second_message=second_message.message_id)
        await SendPayments_StatesGroup.send_user.set()


@dp.message_handler(state=SendPayments_StatesGroup.send_creator)
async def sendPayments_send_creator_handler(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    await message.delete()
    data = await state.get_data()
    deal = await database.get_deal(data['deal_deal_id'])
    if len(message.text) <= 200:
        await database.update_payment_deal(deal.id, message.text)
        deal_text = "покупки" if deal.is_sell else "продаже"
        deal_text_second = "покупаете" if deal.is_sell else "продаёте"
        market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
        subcategory = await database.get_subcategory(deal.subcategory_id)
        category = await database.get_category(deal.category_id)
        key = await confirm_send_payment_creator_deal_keyboard(deal.id)
        await dp.bot.edit_message_text(
            f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
            f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
            f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
            f"<b>{deal.amount_currency} {deal.currency}</b>\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
            f"<b>∙ Реквизиты:</b> <code>{message.text}</code>\n\n"
            f"Вы верно указали реквизиты?\n\n"
            f"<b>⏳ Сделка автоматически закроется, если Вы не ответите в течении 10 минут</b>",
            chat_id=deal.creator_user_id, message_id=deal.creator_mess_id, reply_markup=key)
    else:
        key = await send_payment_creator_deal_keyboard(deal.id)
        subcategory = await database.get_subcategory(deal.subcategory_id)
        category = await database.get_category(deal.category_id)
        await dp.bot.edit_message_text(text=f"<b>Максимум 200 символов</b>\n\n"
                                            f"👉 Пришлите реквизиты для принятия <b>{deal.currency}</b> на {subcategory.name} ({category.name}):",
                                       chat_id=deal.creator_user_id, message_id=deal.creator_mess_id, reply_markup=key)
        await SendPayments_StatesGroup.send_creator.set()


@dp.callback_query_handler(text_startswith='changeCreatorPaymentDeal', state='*')
async def changeCreatorPaymentDeal_handler(call: types.CallbackQuery, state: FSMContext):
    deal = await database.get_deal(call.data.split()[1])
    key = await send_payment_creator_deal_keyboard(deal.id)
    await state.update_data(deal_deal_id=deal.id)
    subcategory = await database.get_subcategory(deal.subcategory_id)
    category = await database.get_category(deal.category_id)
    await call.message.edit_text(
        f"👉 Пришлите реквизиты для принятия <b>{deal.currency}</b> на {subcategory.name} ({category.name}):",
        reply_markup=key)
    await SendPayments_StatesGroup.send_creator.set()


@dp.callback_query_handler(text_startswith='confirmCreatorPaymentDeal', state='*')
async def confirmCreatorPaymentDeal_handler(call: types.CallbackQuery, state: FSMContext):
    deal = await database.get_deal(call.data.split()[1])
    deal_text = "покупки" if deal.is_sell else "продаже"
    deal_text_second = "покупаете" if deal.is_sell else "продаёте"
    market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
    subcategory = await database.get_subcategory(deal.subcategory_id)
    category = await database.get_category(deal.category_id)
    await call.message.edit_text(
        f"<b>Ожидайте перевод.</b>\n\n"
        f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
        f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
        f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
        f"<b>{deal.amount_currency} {deal.currency}</b>\n"
        f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
        f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
        f"<b>⏳ Сделка автоматически отменится, если контрагент не переведёт в течении 30 минут</b>")
    try:
        await dp.bot.delete_message(deal.user_id, deal.user_mess_id)
    except:
        pass
    deal_text = "покупки" if not deal.is_sell else "продаже"
    deal_text_second = "покупаете" if not deal.is_sell else "продаёте"
    market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"
    key = await confirm_transfer_user_deal_keyboard(deal.id)
    user_mess = await dp.bot.send_message(deal.user_id, f"<b>Контрагент подтвердил начало сделки.</b>\n\n"
                                                        f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
                                                        f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                        f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                        f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                        f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                                                        f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
                                                        f"Переведите деньги на указанные реквизиты ⤴\n\n"
                                                        f"<b>⏳ Сделка автоматически отменится, если Вы не переведёте в течении 30 минут</b>",
                                          reply_markup=key)
    await database.update_message_deal(deal_id=deal.id, user_mess_id=user_mess.message_id)
