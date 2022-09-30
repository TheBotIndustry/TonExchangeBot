from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.deal import confirm_transfer_creator_deal_keyboard, yes_confirm_transfer_creator_deal_keyboard
from loader import dp, database


@dp.callback_query_handler(text_startswith='confirmTransferUserDeal', state='*')
async def confirmTransferUserDeal_handler(call: types.CallbackQuery, state: FSMContext):
    deal = await database.get_deal(call.data.split()[1])
    deal_text = "покупки" if deal.is_sell else "продаже"
    deal_text_second = "покупаете" if deal.is_sell else "продаёте"
    market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
    subcategory = await database.get_subcategory(deal.subcategory_id)
    category = await database.get_category(deal.category_id)
    if deal.is_sell:
        await call.message.edit_text(
            f"<b>Вы подтвердили перевод. Ожидайте подтверждения перевода от контрагента.</b>\n\n"
            f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
            f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
            f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
            f"<b>{deal.amount_currency} {deal.currency}</b>\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
            f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
            f"<b>⏳ Вы сможете открыть арбитраж, если контрагент не потдвердит в течении 30 минут</b>")
        try:
            await dp.bot.delete_message(deal.user_id, deal.user_mess_id)
        except:
            pass
        deal_text = "покупки" if not deal.is_sell else "продаже"
        deal_text_second = "покупаете" if not deal.is_sell else "продаёте"
        market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"
        key = await confirm_transfer_creator_deal_keyboard(deal.id)
        user_mess = await dp.bot.send_message(deal.user_id, f"<b>Контрагент подтвердил перевод.</b>\n\n"
                                                            f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
                                                            f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                            f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                            f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                                                            f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
                                                            f"Проверьте наличие {deal.amount_currency} {deal.currency} на указанных реквизитах ⤴\n\n"
                                                            f"⚠  Если перевод ещё не поступил, подождите немного.\n\n"
                                                            f"<b>⏳ Контрагент сможет открыть арбитраж через 30 минут, если Вы не подтвердите перевод</b>",
                                              reply_markup=key)
        await database.update_message_deal(deal_id=deal.id, user_mess_id=user_mess.message_id)
    else:
        deal_text = "покупки" if not deal.is_sell else "продаже"
        deal_text_second = "покупаете" if not deal.is_sell else "продаёте"
        market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"
        await call.message.edit_text(
            f"<b>Вы подтвердили перевод. Ожидайте подтверждения перевода от контрагента.</b>\n\n"
            f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
            f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
            f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
            f"<b>{deal.amount_currency} {deal.currency}</b>\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
            f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
            f"<b>⏳ Вы сможете открыть арбитраж, если контрагент не потдвердит в течении 30 минут</b>")
        try:
            await dp.bot.delete_message(deal.creator_user_id, deal.creator_mess_id)
        except:
            pass
        deal_text = "покупки" if deal.is_sell else "продаже"
        deal_text_second = "покупаете" if deal.is_sell else "продаёте"
        market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
        key = await confirm_transfer_creator_deal_keyboard(deal.id)
        user_creator = await dp.bot.send_message(deal.creator_user_id, f"<b>Контрагент подтвердил перевод.</b>\n\n"
                                                                       f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
                                                                       f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                                       f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                                       f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                                       f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                                                                       f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
                                                                       f"Проверьте наличие {deal.amount_currency} {deal.currency} на указанных реквизитах ⤴\n\n"
                                                                       f"⚠  Если перевод ещё не поступил, подождите немного.\n\n"
                                                                       f"<b>⏳ Контрагент сможет открыть арбитраж через 30 минут, если Вы не подтвердите перевод</b>",
                                                 reply_markup=key)
        await database.update_message_deal(deal_id=deal.id, creator_mess_id=user_creator.message_id)


@dp.callback_query_handler(text_startswith='confirmTransferCreatorDeal', state='*')
async def confirmTransferCreatorDeal_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    deal = await database.get_deal(call.data.split()[1])
    if deal.is_sell:
        deal_text = "покупки" if not deal.is_sell else "продаже"
        deal_text_second = "покупаете" if not deal.is_sell else "продаёте"
        market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"
    else:
        deal_text = "покупки" if deal.is_sell else "продаже"
        deal_text_second = "покупаете" if deal.is_sell else "продаёте"
        market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
    subcategory = await database.get_subcategory(deal.subcategory_id)
    category = await database.get_category(deal.category_id)
    key = await yes_confirm_transfer_creator_deal_keyboard(deal.id)
    await call.message.edit_text(f"<b>Контрагент подтвердил перевод.</b>\n\n"
                                 f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
                                 f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                 f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                 f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                 f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                                 f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
                                 f"Проверьте наличие {deal.amount_currency} {deal.currency} на указанных реквизитах ⤴\n\n"
                                 f"⚠  Вы уверены, что получили {deal.amount_currency} {deal.currency} по реквизитам <code>{deal.payment}</code>?",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='yesConfirmTransferCreatorDeal', state='*')
async def yesConfirmTransferCreatorDeal_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    deal = await database.get_deal(call.data.split()[1])
    await database.finish_deal(deal.id)

    try:
        await dp.bot.delete_message(deal.creator_user_id, deal.creator_mess_id)
    except:
        pass
    try:
        await dp.bot.delete_message(deal.user_id, deal.user_mess_id)
    except:
        pass

    subcategory = await database.get_subcategory(deal.subcategory_id)
    category = await database.get_category(deal.category_id)
    if deal.is_sell:
        deal_text_creator = "покупки" if deal.is_sell else "продаже"
        deal_text_second_creator = "купили" if deal.is_sell else "продали"
        market_sell_or_buy_text_creator = "отправки" if deal.is_sell else "принятия"

        deal_text_user = "покупки" if not deal.is_sell else "продаже"
        deal_text_second_user = "купили" if not deal.is_sell else "продали"
        market_sell_or_buy_text_user = "отправки" if not deal.is_sell else "принятия"

        try:
            await dp.bot.send_message(deal.creator_user_id,
                                      f"✅ Сделка по <b>{deal_text_creator} {deal.cryptocurrency}</b> за <b>{deal.currency}</b> завершена.\n\n"
                                      f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                      f"Вы <b><u>{deal_text_second_creator}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                      f"<b>{deal.amount_currency} {deal.currency}</b>\n\n"
                                      f"<b>∙ Способ {market_sell_or_buy_text_creator} денег:</b> {subcategory.name} ({category.name})\n"
                                      f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>")
        except:
            pass

        try:
            await dp.bot.send_message(deal.user_id,
                                      f"✅ Сделка по <b>{deal_text_user} {deal.cryptocurrency}</b> за <b>{deal.currency}</b> завершена.\n\n"
                                      f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                      f"Вы <b><u>{deal_text_second_user}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                      f"<b>{deal.amount_currency} {deal.currency}</b>\n\n"
                                      f"<b>∙ Способ {market_sell_or_buy_text_user} денег:</b> {subcategory.name} ({category.name})\n"
                                      f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>")
        except:
            pass
    else:
        deal_text_creator = "покупки" if deal.is_sell else "продаже"
        deal_text_second_creator = "купили" if deal.is_sell else "продали"
        market_sell_or_buy_text_creator = "отправки" if deal.is_sell else "принятия"

        deal_text_user = "покупки" if not deal.is_sell else "продаже"
        deal_text_second_user = "купили" if not deal.is_sell else "продали"
        market_sell_or_buy_text_user = "отправки" if not deal.is_sell else "принятия"

        try:
            await dp.bot.send_message(deal.creator_user_id,
                                      f"✅ Сделка по <b>{deal_text_creator} {deal.cryptocurrency}</b> за <b>{deal.currency}</b> завершена.\n\n"
                                      f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                      f"Вы <b><u>{deal_text_second_creator}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                      f"<b>{deal.amount_currency} {deal.currency}</b>\n\n"
                                      f"<b>∙ Способ {market_sell_or_buy_text_creator} денег:</b> {subcategory.name} ({category.name})\n"
                                      f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>")
        except:
            pass

        try:
            await dp.bot.send_message(deal.user_id,
                                      f"✅ Сделка по <b>{deal_text_user} {deal.cryptocurrency}</b> за <b>{deal.currency}</b> завершена.\n\n"
                                      f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                      f"Вы <b><u>{deal_text_second_user}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                      f"<b>{deal.amount_currency} {deal.currency}</b>\n\n"
                                      f"<b>∙ Способ {market_sell_or_buy_text_user} денег:</b> {subcategory.name} ({category.name})\n"
                                      f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>")
        except:
            pass
