from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.deal.sendPayments import SendPayments_StatesGroup
from keyboards.deal import send_payment_creator_deal_keyboard, confirm_transfer_user_deal_keyboard
from loader import dp, database


@dp.callback_query_handler(text_startswith='startDealCreate', state='*')
async def startDealCreate_handler(call: types.CallbackQuery, state: FSMContext):
    deal_id = call.data.split()[1]
    deal = await database.get_deal(deal_id)
    await state.update_data(deal_deal_id=deal.id)
    subcategory = await database.get_subcategory(deal.subcategory_id)
    category = await database.get_category(deal.category_id)
    if deal.creator_user_id == call.message.chat.id:
        balance = await database.get_balance_user(deal.creator_user_id, deal.cryptocurrency)
        if balance >= deal.amount_crypto:
            await database.run_deposit(deal.id, deal.creator_user_id, deal.cryptocurrency, deal.amount_crypto)
            key = await send_payment_creator_deal_keyboard(deal.id)
            await call.message.edit_text(
                f"👉 Пришлите реквизиты для принятия <b>{deal.currency}</b> на {subcategory.name} ({category.name}):",
                reply_markup=key)
            await SendPayments_StatesGroup.send_creator.set()
        else:
            await call.answer("У Вас недостаточно баланса для открытия сделки.\n\n"
                              f"Необходимо: {deal.amount_crypto} {deal.cryptocurrency}", show_alert=True)
            return
    else:

        await database.start_deal(deal.id)

        deal_text = "покупки" if deal.is_sell else "продаже"
        deal_text_second = "покупаете" if deal.is_sell else "продаёте"
        market_sell_or_buy_text = "отправки" if deal.is_sell else "принятия"
        key = await confirm_transfer_user_deal_keyboard(deal.id)
        await call.message.edit_text(f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
                                     f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                     f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                     f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                     f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                                     f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
                                     f"Переведите деньги на указанные реквизиты ⤴\n\n"
                                     f"<b>⏳ Сделка автоматически отменится, если Вы не переведёте в течении 30 минут</b>",
                                     reply_markup=key)
        try:
            await dp.bot.delete_message(deal.user_id, deal.user_mess_id)
        except:
            pass
        deal_text = "покупки" if not deal.is_sell else "продаже"
        deal_text_second = "покупаете" if not deal.is_sell else "продаёте"
        market_sell_or_buy_text = "отправки" if not deal.is_sell else "принятия"
        user_mess = await dp.bot.send_message(deal.user_id, f"<b>Ожидайте перевод.</b>\n\n"
                                                            f"Сделка по <b>{deal_text} {deal.cryptocurrency}</b> за <b>{deal.currency}</b>.\n\n"
                                                            f"<b>∙ Номер сделки:</b> {deal.id}\n\n"
                                                            f"<b>∙ Условия:</b> Вы <b><u>{deal_text_second}</u> {deal.amount_crypto} {deal.cryptocurrency}</b> за "
                                                            f"<b>{deal.amount_currency} {deal.currency}</b>\n"
                                                            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n"
                                                            f"<b>∙ Реквизиты:</b> <code>{deal.payment}</code>\n\n"
                                                            f"<b>⏳ Сделка автоматически отменится, если контрагент не переведёт в течении 30 минут</b>")
        await database.update_message_deal(deal_id=deal.id, user_mess_id=user_mess.message_id)
