from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.start import starting_keyboard
from loader import dp, database
from utils.other.messages import delete_first_second_messages


@dp.message_handler(commands=('start', 'menu'), state='*')
async def command_start(message: types.Message, state: FSMContext):
    await message.delete()
    if not await database.get_user(message.chat.id):
        await database.add_user(message.chat.id, message.chat.full_name)
        await state.update_data(filterMyAdvert="All")
        await message.answer("<b>💱 VIVA CHANGE</b>")
    await state.reset_state(False)
    await state.update_data(in_market=None)
    data = await state.get_data()
    key = await starting_keyboard()
    await delete_first_second_messages(message.chat.id, data)
    first_message = await message.answer("👛", reply_markup=key)
    second_message = await message.answer("МультиВалютный обменник")
    await state.update_data(first_message=first_message.message_id,
                            second_message=second_message.message_id)
