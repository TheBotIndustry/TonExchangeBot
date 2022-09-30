from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.deal import deal_cryptocurrency_keyboard, deal_currency_keyboard, deal_categories_keyboard, \
    deal_subcategories_keyboard, deal_adverts_keyboard
from loader import dp, database


@dp.callback_query_handler(text_startswith="cripto_", state='*')
async def cripto_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    await state.update_data(selectExchange=True)
    market_is_sell = True if call.data.split("_")[1] == 'sell' else False
    market_text = "Купить" if not market_is_sell else "Продать"
    market_text_second = "покупки" if not market_is_sell else "продажи"
    await state.update_data(market_is_sell=market_is_sell, market_text=market_text, in_market=True)
    await state.update_data(market_cryptocurrency=None, market_currency=None, market_category_id=None,
                            market_subcategory_id=None)
    key = await deal_cryptocurrency_keyboard()
    await call.message.edit_text(f"<b>{market_text}</b>\n\n"
                                 f"👉 Выберите криптовалюту для {market_text_second}:",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='dealCryptocurrency_', state='*')
async def dealCryptocurrency_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    market_cryptocurrency = call.data.split("_")[1]
    await state.update_data(market_cryptocurrency=market_cryptocurrency)
    await state.update_data(market_currency=None, market_category_id=None,
                            market_subcategory_id=None)
    key = await deal_currency_keyboard(data['market_is_sell'])
    await call.message.edit_text(f"<b>{data['market_text']} {market_cryptocurrency}</b>\n\n"
                                 f"👉 Выберите валюту, в которой хотите провести операцию:",
                                 reply_markup=key)


@dp.callback_query_handler(text_startswith='dealCurrency_', state='*')
async def dealCurrency_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    market_currency = call.data.split("_")[1]
    await state.update_data(market_currency=market_currency)
    await state.update_data(market_category_id=None,
                            market_subcategory_id=None)
    adverts = await database.get_categories_market(market_is_sell=data['market_is_sell'], currency=market_currency,
                                                   cryptocurrency=data['market_cryptocurrency'])
    if not adverts:
        await call.answer("🤷 В этом разделе ещё нет объявлений, но Вы можете их создать",
                          show_alert=True)
    else:
        market_sell_or_buy_text = "принимать" if data['market_is_sell'] == True else "отправлять"
        key = await deal_categories_keyboard(data['market_cryptocurrency'], adverts)
        await call.message.edit_text(
            f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{market_currency}</b>\n\n"
            f"👉 Выберите раздел, в котором удобнее будет {market_sell_or_buy_text} деньги:",
            reply_markup=key)


@dp.callback_query_handler(text_startswith='dealCategory_', state='*')
async def dealCategory_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    market_category_id = call.data.split("_")[1]
    await state.update_data(market_category_id=market_category_id)
    await state.update_data(market_subcategory_id=None)
    category = await database.get_category(market_category_id)
    adverts = await database.get_subcategories_market(market_is_sell=data['market_is_sell'],
                                                      currency=data['market_currency'],
                                                      category_id=market_category_id,
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


@dp.callback_query_handler(text_startswith='dealSubcategory_', state='*')
async def dealSubcategory_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    market_subcategory_id = call.data.split("_")[1]
    await state.update_data(market_subcategory_id=market_subcategory_id)
    await state.update_data(filterAdvertAmount=None)
    data = await state.get_data()
    category = await database.get_category(data['market_category_id'])
    subcategory = await database.get_subcategory(market_subcategory_id)
    adverts = await database.get_adverts_market(market_is_sell=data['market_is_sell'],
                                                currency=data['market_currency'],
                                                subcategory_id=market_subcategory_id,
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
        key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                          call.message.chat.id, data['filterAdvertAmount'], 1)
        await call.message.edit_text(
            f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
            f"👉 Выберите подходящее объявление:\n\n"
            f"<i>Ваши объявления со знаком «🔷».</i>",
            reply_markup=key)
