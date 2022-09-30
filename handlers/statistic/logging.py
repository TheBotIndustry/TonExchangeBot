import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.handler import SkipHandler

from loader import dp


@dp.message_handler(content_types=('text',), state='*')
async def logging_handler(message: types.Message, state: FSMContext):
    state = await state.get_state()
    user_id = message.chat.id
    date = datetime.datetime.now()
    # if state is None:
        # print(f'{message.chat.full_name} ({user_id}) {date.day}.{date.month}.{date.year} в {date.hour}:{date.minute} нажал кнопку «{message.text}»')
    # else:
    #     print(f'{message.chat.full_name} ({user_id}) {date.day}.{date.month}.{date.year} в {date.hour}:{date.minute} ввёл «{message.text}»')
    raise SkipHandler


@dp.callback_query_handler(state='*')
async def logging_callback_handler(call: types.CallbackQuery, state: FSMContext):
    state = await state.get_state()
    user_id = call.message.chat.id
    date = datetime.datetime.now()
    buttons = call.message.reply_markup.inline_keyboard
    name_button = ''
    for button_row in buttons:
        for button in button_row:
            if button.callback_data == call.data:
                name_button = button.text
                break
    # print(f'{call.message.chat.full_name} ({user_id}) {date.day}.{date.month}.{date.year} в {date.hour}:{date.minute} нажал кнопку «{name_button}»')
    raise SkipHandler
