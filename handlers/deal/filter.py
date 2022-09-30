from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from keyboards.deal import filter_advert_amount_keyboard, deal_currency_keyboard, deal_adverts_keyboard
from keyboards.start import starting_keyboard
from loader import dp, database
from utils.other.messages import delete_first_second_messages


class FilterAdvertStatesGroup(StatesGroup):
    enter_amount = State()


@dp.callback_query_handler(text="FilterSetDealAdvert", state="*")
async def FilterSetDealAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    await delete_first_second_messages(call.message.chat.id, data)
    await state.update_data(filterAdvertAmountSelect=data['market_cryptocurrency'])
    key = await filter_advert_amount_keyboard(data['market_currency'])
    first_message = await call.message.answer("💸", reply_markup=key)
    category = await database.get_category(data['market_category_id'])
    subcategory = await database.get_subcategory(data['market_subcategory_id'])
    market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
    filter_sell_or_buy_text = "продать" if data['market_is_sell'] == True else "купить"
    second_message = await call.message.answer(
        f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
        f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
        f"👉 Введите в <b>{data['market_cryptocurrency']}</b> сколько хотите {filter_sell_or_buy_text}\n\n"
        f"⚠ Если Вы хотите указать сумму в {data['market_currency']}, нажми кнопку ниже")
    await state.update_data(first_message=first_message.message_id, second_message=second_message.message_id)
    await FilterAdvertStatesGroup.enter_amount.set()


@dp.message_handler(text="❌ Отменить", state="*")
async def cancel_filter_amount_handler(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    await message.delete()
    data = await state.get_data()
    await delete_first_second_messages(message.chat.id, data)
    category = await database.get_category(data['market_category_id'])
    subcategory = await database.get_subcategory(data['market_subcategory_id'])
    adverts = await database.get_adverts_market(market_is_sell=data['market_is_sell'],
                                                currency=data['market_currency'],
                                                subcategory_id=data['market_subcategory_id'],
                                                cryptocurrency=data['market_cryptocurrency'])
    key = await starting_keyboard()
    first_message = await message.answer("💸", reply_markup=key)
    if not adverts:
        key = await deal_currency_keyboard(data['market_is_sell'])
        second_message = await message.answer(f"<b>🤷 В этом разделе ещё нет объявлений</b>\n\n"
                                              f"<b>{data['market_text']} {data['market_cryptocurrency']}</b>\n\n"
                                              f"👉 Выберите валюту, в которой хотите провести операцию:",
                                              reply_markup=key)
        await state.update_data(market_currency=None, market_category_id=None,
                                market_subcategory_id=None)
    else:
        market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
        key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                          message.chat.id, data['filterAdvertAmount'], 1)
        second_message = await message.answer(
            f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
            f"👉 Выберите подходящее объявление:\n\n"
            f"<i>Ваши объявления со знаком «🔷».</i>",
            reply_markup=key)
    await state.update_data(first_message=first_message.message_id, second_message=second_message.message_id)


@dp.message_handler(text_startswith="Указать в ", state="*")
async def cancel_filter_amount_handler(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    await message.delete()
    data = await state.get_data()
    await delete_first_second_messages(message.chat.id, data)
    filterAdvertAmountSelect = message.text.split("Указать в ")[-1]
    filterAdvertAmountSelectNext = data['market_currency'] if filterAdvertAmountSelect == data[
        'market_cryptocurrency'] else data['market_cryptocurrency']
    await state.update_data(filterAdvertAmountSelect=filterAdvertAmountSelect)
    category = await database.get_category(data['market_category_id'])
    subcategory = await database.get_subcategory(data['market_subcategory_id'])
    market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
    filter_sell_or_buy_text = "продать" if data['market_is_sell'] == True else "купить"
    key = await filter_advert_amount_keyboard(filterAdvertAmountSelectNext)
    first_message = await message.answer("💸", reply_markup=key)
    second_message = await message.answer(
        f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
        f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
        f"👉 Введите в <b>{filterAdvertAmountSelect}</b> сколько хотите {filter_sell_or_buy_text}\n\n"
        f"⚠ Если Вы хотите указать сумму в {filterAdvertAmountSelectNext}, нажмите кнопку ниже")
    await state.update_data(first_message=first_message.message_id, second_message=second_message.message_id)
    await FilterAdvertStatesGroup.enter_amount.set()


@dp.message_handler(state=FilterAdvertStatesGroup.enter_amount)
async def filterAdvertState_enter_amount(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    await message.delete()
    data = await state.get_data()
    await delete_first_second_messages(message.chat.id, data)
    filterAdvertAmountSelect = data['filterAdvertAmountSelect']
    await state.update_data(filterAdvertAmount=filterAdvertAmountSelect)
    data = await state.get_data()
    category = await database.get_category(data['market_category_id'])
    subcategory = await database.get_subcategory(data['market_subcategory_id'])
    try:
        amount = float(message.text)
        await state.update_data(filterAdvertCount=amount)
        adverts = await database.get_adverts_filter_market(market_is_sell=data['market_is_sell'],
                                                           currency=data['market_currency'],
                                                           subcategory_id=data['market_subcategory_id'],
                                                           cryptocurrency=data['market_cryptocurrency'],
                                                           filter_parameter=filterAdvertAmountSelect,
                                                           amount_parameter=amount)
        key = await starting_keyboard()
        first_message = await message.answer("💸", reply_markup=key)
        market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
        key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                          message.chat.id, data['filterAdvertAmount'], amount)
        second_message = await message.answer(
            f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
            f"👉 Выберите подходящее объявление:\n\n"
            f"<i>Ваши объявления со знаком «🔷».</i>",
            reply_markup=key)
        await state.update_data(first_message=first_message.message_id, second_message=second_message.message_id)
    except Exception as e:
        print(e)
        market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
        filter_sell_or_buy_text = "продать" if data['market_is_sell'] == True else "купить"
        filterAdvertAmountSelectNext = data['market_currency'] if filterAdvertAmountSelect == data[
            'market_cryptocurrency'] else data['market_cryptocurrency']
        key = await filter_advert_amount_keyboard(filterAdvertAmountSelectNext)
        first_message = await message.answer("💸", reply_markup=key)
        second_message = await message.answer(
            f"<b>Ошибка ввода!</b>\n\n"
            f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
            f"👉 Введите в <b>{filterAdvertAmountSelect}</b> сколько хотите {filter_sell_or_buy_text}\n\n"
            f"⚠ Если Вы хотите указать сумму в {filterAdvertAmountSelectNext}, нажмите кнопку ниже")
        await state.update_data(first_message=first_message.message_id, second_message=second_message.message_id)
        await FilterAdvertStatesGroup.enter_amount.set()


@dp.callback_query_handler(text="FilterResetDealAdvert", state="*")
async def FilterResetDealAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    await state.update_data(filterAdvertAmount=None)
    data = await state.get_data()
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
        market_sell_or_buy_text = "принятия" if data['market_is_sell'] == True else "отправки"
        key = await deal_adverts_keyboard(data['market_category_id'], adverts, data['market_currency'],
                                          call.message.chat.id, data['filterAdvertAmount'], 1)
        await call.message.edit_text(
            f"<b>{data['market_text']} {data['market_cryptocurrency']}</b> за <b>{data['market_currency']}</b>\n\n"
            f"<b>∙ Способ {market_sell_or_buy_text} денег:</b> {subcategory.name} ({category.name})\n\n"
            f"👉 Выберите подходящее объявление:\n\n"
            f"<i>Ваши объявления со знаком «🔷».</i>",
            reply_markup=key)
