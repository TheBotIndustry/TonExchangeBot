from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.deal import deal_currency_keyboard, deal_adverts_keyboard, deal_subcategories_keyboard, \
    deal_categories_keyboard, deal_cryptocurrency_keyboard
from loader import dp, database


@dp.callback_query_handler(text="continueWatchAdvert", state='*')
async def continueWatchAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    await state.update_data(selectExchange=True)
    data = await state.get_data()
    if data.get('market_subcategory_id'):
        category = await database.get_category(data['market_category_id'])
        subcategory = await database.get_subcategory(data['market_subcategory_id'])
        adverts = await database.get_adverts_market(market_is_sell=data['market_is_sell'],
                                                    currency=data['market_currency'],
                                                    subcategory_id=data['market_subcategory_id'],
                                                    cryptocurrency=data['market_cryptocurrency'])
        if not adverts:
            key = await deal_currency_keyboard(data['market_is_sell'])
            await call.message.edit_text(f"<b>🤷 В этом разделе ещё нет объявлений</b>\n\n"
                                         f"<b>{data['market_text']} {data['market_cryptocurrency']}</b>\n\n"
                                         f"👉 Выберите валюту, в которой хотите провести операцию:",
                                         reply_markup=key)
            await state.update_data(market_currency=None, market_category_id=None,
                                    market_subcategory_id=None)
        else:
            await state.update_data(filterAdvertAmount=None)
            data = await state.get_data()
            market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
            key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                              call.message.chat.id, data['filterAdvertAmount'], 1)
            await call.message.edit_text(
                f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
                f"👉 Выберите подходящее объявление:\n\n"
                f"<i>Ваши объявления со знаком «🔷».</i>",
                reply_markup=key)
    elif data.get('market_category_id'):
        category = await database.get_category(data['market_category_id'])
        adverts = await database.get_subcategories_market(market_is_sell=data['market_is_sell'],
                                                          currency=data['market_currency'],
                                                          category_id=data['market_category_id'],
                                                          cryptocurrency=data['market_cryptocurrency'])
        if not adverts:
            key = await deal_currency_keyboard(data['market_is_sell'])
            await call.message.edit_text(f"<b>🤷 В этом разделе ещё нет объявлений</b>\n\n"
                                         f"<b>{data['market_text']} {data['market_cryptocurrency']}</b>\n\n"
                                         f"👉 Выберите валюту, в которой хотите провести операцию:",
                                         reply_markup=key)
            await state.update_data(market_currency=None, market_category_id=None,
                                    market_subcategory_id=None)
        else:
            market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
            key = await deal_subcategories_keyboard(data['market_currency'], adverts)
            await call.message.edit_text(
                f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b> ({category.name})\n\n"
                f"👉 Выберите удобный способ {market_sell_or_buy_text} денег:",
                reply_markup=key)
    elif data.get('market_currency'):
        adverts = await database.get_categories_market(market_is_sell=data['market_is_sell'], currency=data['market_currency'],
                                                       cryptocurrency=data['market_cryptocurrency'])
        if not adverts:
            await call.answer("🤷 В этом разделе ещё нет объявлений, но Вы можешь их создать",
                              show_alert=True)
        else:
            market_sell_or_buy_text = "принимать" if data['market_is_sell'] == True else "отправлять"
            key = await deal_categories_keyboard(data['market_cryptocurrency'], adverts)
            await call.message.edit_text(
                f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
                f"👉 Выберите раздел, в котором удобнее будет {market_sell_or_buy_text} деньги:",
                reply_markup=key)
    elif data.get('market_cryptocurrency'):
        key = await deal_currency_keyboard(data['market_is_sell'])
        await call.message.edit_text(f"<b>{data['market_text']} {data['market_cryptocurrency']}</b>\n\n"
                                     f"👉 Выберите валюту, в которой хотите провести операцию:",
                                     reply_markup=key)
    else:
        key = await deal_cryptocurrency_keyboard()
        market_text_second = "покупки" if not data['market_is_sell'] else "продажи"
        await call.message.edit_text(f"<b>{data['market_text']}</b>\n\n"
                                     f"👉 Выберите криптовалюту для {market_text_second}:",
                                     reply_markup=key)
