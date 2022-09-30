from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.profile import profile_keyboard
from keyboards.start import starting_keyboard
from loader import dp, database
from utils.other.messages import delete_first_second_messages
from utils.other.operations_with_cryptocurrency import amount_in_dollars, makeRoundFloatDollars
from utils.other.operations_with_date import with_us_naming


@dp.message_handler(text="💎 Мой профиль", state='*')
async def my_profile_button(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    await state.update_data(in_market=None)
    await message.delete()
    data = await state.get_data()
    await delete_first_second_messages(message.chat.id, data)
    key = await starting_keyboard()
    first_message = await message.answer("💎", reply_markup=key)
    user = await database.get_user(message.chat.id)
    key_second = await profile_keyboard()
    second_message = await message.answer(f"<b>💎 Мой профиль</b>\n\n"
                                          f"∙ <a href='https://coinmarketcap.com/currencies/toncoin/'>TON:</a> {await makeRoundFloatDollars(user.balance_toncoin)}\n\n"
                                          f"<b>Примерный баланс:</b> ${await amount_in_dollars(user)}",
                                          disable_web_page_preview=True,
                                          reply_markup=key_second)
    await state.update_data(first_message=first_message.message_id,
                            second_message=second_message.message_id)


@dp.callback_query_handler(text="more_information", state='*')
async def more_information_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    user = await database.get_user(call.message.chat.id)
    key_second = await profile_keyboard(True)
    await call.message.edit_text(f"<b>💎 Мой профиль</b>\n\n"
                                 f"∙ <a href='https://coinmarketcap.com/currencies/toncoin/'>TON:</a> {await makeRoundFloatDollars(user.balance_toncoin)}\n\n"
                                 f"<b>Примерный баланс:</b> ${await amount_in_dollars(user)}\n\n"
                                 f"<b>Сделок:</b> {user.count_deals}\n\n"
                                 f"<b>🗓 С нами с {await with_us_naming(user.date_registration)}</b>",
                                 disable_web_page_preview=True,
                                 reply_markup=key_second)


@dp.callback_query_handler(text="less_information", state='*')
async def less_information_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    user = await database.get_user(call.message.chat.id)
    key_second = await profile_keyboard()
    await call.message.edit_text(f"<b>💎 Мой профиль</b>\n\n"
                                 f"∙ <a href='https://coinmarketcap.com/currencies/toncoin/'>TON:</a> {await makeRoundFloatDollars(user.balance_toncoin)}\n\n"
                                 f"<b>Примерный баланс:</b> ${await amount_in_dollars(user)}",
                                 disable_web_page_preview=True,
                                 reply_markup=key_second)
