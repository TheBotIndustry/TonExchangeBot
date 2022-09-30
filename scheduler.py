from loader import database


async def update_course():
    await database.update_course_in_database()
