from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.exchange import exchange_keyboard
from keyboards.start import starting_keyboard
from loader import dp
from utils.other.messages import delete_first_second_messages


@dp.message_handler(text='🔄 Обмен', state='*')
async def exchange_button(message: types.Message, state: FSMContext):
    await state.reset_state(False)
    await state.update_data(in_market=None)
    await message.delete()
    data = await state.get_data()
    await delete_first_second_messages(message.chat.id, data)
    key = await starting_keyboard()
    first_message = await message.answer("💸", reply_markup=key)
    key_second = await exchange_keyboard(data)
    second_message = await message.answer(f"<b>🔄 Обмен</b>\n\n"
                                          f"💸 Вы можете купить/продать криптовалюту или создать своё объявление.",
                                          reply_markup=key_second)
    await state.update_data(first_message=first_message.message_id,
                            second_message=second_message.message_id)


@dp.callback_query_handler(text='back_to_exchange', state='*')
async def back_to_exchange_handler(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state(False)
    data = await state.get_data()
    key = await exchange_keyboard(data)
    await call.message.edit_text(f"<b>🔄 Обмен</b>\n\n"
                                 f"💸 Вы можешь купить/продать криптовалюту или создать своё объявление.",
                                 reply_markup=key)
