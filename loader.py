from aiogram import Bot, types, Dispatcher
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from config import token
from utils.database_api.commands.main import DB_Commands

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=RedisStorage2())
database = DB_Commands()
