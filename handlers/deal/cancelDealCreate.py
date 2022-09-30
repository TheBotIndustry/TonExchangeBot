from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, database


@dp.callback_query_handler(text_startswith='cancelDealCreate', state='*')
async def cancelDealCreate_handler(call: types.CallbackQuery, state: FSMContext):
    deal_id = call.data.split()[1]
    deal = await database.get_deal(deal_id)
    subcategory = await database.get_subcategory(deal.subcategory_id)
    category = await database.get_category(deal.category_id)
    if deal.user_id == call.message.chat.id:
        try:
            deal_is_sell_text = "продаёте" if deal.is_sell else "покупаете"
            market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"
            await dp.bot.edit_message_text(text="<b>❌ Вы отменили следующую сделку:</b>\n\n"
                                                f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                f"<b>∙ Условия:</b> Вы <b><u>{deal_is_sell_text}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})",
                                           chat_id=deal.user_id,
                                           message_id=deal.user_mess_id)
        except:
            pass
        if deal.is_sell:
            await database.get_back_deposit(deal.user_id, deal.cryptocurrency, deal.amount_crypto)
        else:
            if deal.is_deposit_for_sell:
                await database.get_back_deposit(deal.creator_user_id, deal.cryptocurrency, deal.amount_crypto)
        try:
            deal_text_second = "покупаете" if deal.is_sell else "продаёте"
            market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
            await dp.bot.edit_message_text(text="<b>❌ Вам была предложена и через некоторое время отменена следующая сделка:</b>\n\n"
                                                f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})",
                                           chat_id=deal.creator_user_id,
                                           message_id=deal.creator_mess_id)
        except:
            pass
    else:
        try:
            deal_is_sell_text = "продаёте" if deal.is_sell else "покупаете"
            market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"
            await dp.bot.edit_message_text(text="<b>❌ Контрагент отказался от следующей сделки:</b>\n\n"
                                                f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                f"<b>∙ Условия:</b> Вы <b><u>{deal_is_sell_text}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})",
                                           chat_id=deal.user_id,
                                           message_id=deal.user_mess_id)
        except:
            pass
        if deal.is_sell:
            await database.get_back_deposit(deal.user_id, deal.cryptocurrency, deal.amount_crypto)
        else:
            if deal.is_deposit_for_sell:
                await database.get_back_deposit(deal.creator_user_id, deal.cryptocurrency, deal.amount_crypto)
        try:
            deal_text_second = "покупаете" if deal.is_sell else "продаёте"
            market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
            await dp.bot.edit_message_text(
                text="<b>❌ Вы отказались от следующей сделки:</b>\n\n"
                     f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                     f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                     f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                     f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})",
                chat_id=deal.creator_user_id,
                message_id=deal.creator_mess_id)
        except:
            pass
    await database.delete_deal(deal.id)
