from aiogram import types


async def setup_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("menu", "Open menu")
        ]
    )
