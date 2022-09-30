from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.exchange import my_adverts_keyboard
from loader import dp, database


@dp.callback_query_handler(text_startswith='filterMyAdvert_', state='*')
async def filterMyAdvert_handler(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(filterMyAdvert=call.data.split("_")[1])
    data = await state.get_data()
    adverts = await database.get_adverts_user(call.message.chat.id, call.data.split("_")[1])
    key = await my_adverts_keyboard(adverts, data)
    if not adverts:
        await call.message.edit_text("<b>🗒 Мои объявления</b>\n\n"
                                     "У Вас ещё нет объявлений.\n\n"
                                     "👌 Можно их создать.",
                                     reply_markup=key)
    else:
        await call.message.edit_text(f"<b>🗒 Мои объявления</b>\n\n"
                                     f"Список Ваших объявлений:",
                                     reply_markup=key)
