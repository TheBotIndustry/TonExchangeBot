import asyncio

import aioschedule
from aiogram.utils.executor import start_polling

from scheduler import update_course
from utils.database_api.commands.courses import DB_Courses
from utils.database_api.main import init_db
from utils.other.def_commands import setup_default_commands


async def scheduler_run():
    aioschedule.every(60).seconds.do(update_course)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_starting_bot(dp):
    await init_db()
    await setup_default_commands(dp)
    await DB_Courses().set_starting_courses()
    asyncio.create_task(scheduler_run())


if __name__ == '__main__':
    from handlers import dp

    start_polling(dp, on_startup=on_starting_bot)
