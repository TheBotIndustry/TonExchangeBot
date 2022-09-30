from gino import Gino

from config import POSTGRES_URL

db_gino = Gino()


async def init_db():
    await db_gino.set_bind(POSTGRES_URL)
