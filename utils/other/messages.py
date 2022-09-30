from typing import Dict

from aiogram.dispatcher import FSMContext

from loader import dp


async def delete_first_second_messages(user_id, data: Dict):
    try:
        await dp.bot.delete_message(user_id, data['first_message'])
    except:
        pass
    try:
        await dp.bot.delete_message(user_id, data['second_message'])
    except:
        pass


async def edit_first_second_messages(user_id, data: Dict, smile, text, key_first, state: FSMContext, key_second=None):
    try:
        await dp.bot.edit_message_text(text=smile, chat_id=user_id, message_id=data['first_message'])
        await dp.bot.edit_message_text(text=text, chat_id=user_id, message_id=data['second_message'], reply_markup=key_second)
    except Exception as e:
        print(e)
        try:
            await dp.bot.delete_message(user_id, data['first_message'])
        except:
            pass
        try:
            await dp.bot.delete_message(user_id, data['second_message'])
        except:
            pass
        first_message = await dp.bot.send_message(chat_id=user_id, text=smile, reply_markup=key_first)
        second_message = await dp.bot.send_message(chat_id=user_id, text=text, reply_markup=key_second)
        await state.update_data(first_message=first_message.message_id,
                                second_message=second_message.message_id)
