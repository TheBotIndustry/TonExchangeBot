from environs import Env

env = Env()
env.read_env()

token = env.str('TOKEN')

POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
POSTGRES_DB = env.str("POSTGRES_DB")
POSTGRES_HOST = env.str("POSTGRES_HOST")
POSTGRES_PORT = env.int("POSTGRES_PORT")
POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"