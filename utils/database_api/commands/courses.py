import aiohttp
from bs4 import BeautifulSoup

from utils.database_api.models.courses import Courses


class DB_Courses:
    async def get_course_toncoin_in_dollars(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://coinmarketcap.com/currencies/toncoin/") as resp:
                response = await resp.text()
                soup = BeautifulSoup(response, 'lxml')
                course = soup.find('div', class_='priceValue').find()
                return float(course.text[1:].replace(',', ''))

    async def get_course_toncoin_in_rubbles(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://coinmarketcap.com/ru/currencies/toncoin/") as resp:
                response = await resp.text()
                soup = BeautifulSoup(response, 'lxml')
                course = soup.find('div', class_='priceValue').find()
                return float(course.text[1:].replace(',', ''))

    async def get_course(self, name) -> Courses:
        return await Courses.query.where(Courses.name == name).gino.first()

    async def set_starting_courses(self):
        # TON
        toncoin = await self.get_course('TON')
        course_toncoin = await self.get_course_toncoin_in_dollars()
        course_rub_toncoin = await self.get_course_toncoin_in_rubbles()
        if toncoin is not None:
            await toncoin.update(course=course_toncoin).apply()
            await toncoin.update(course_rub=course_rub_toncoin).apply()
        else:
            toncoin_create = Courses()
            toncoin_create.name = 'TON'
            toncoin_create.course = course_toncoin
            toncoin_create.course_rub = course_rub_toncoin
            await toncoin_create.create()

    async def update_course_in_database(self):
        # TON
        toncoin = await self.get_course('TON')
        course_toncoin = await self.get_course_toncoin_in_dollars()
        course_rub_toncoin = await self.get_course_toncoin_in_rubbles()
        await toncoin.update(course=course_toncoin).apply()
        await toncoin.update(course_rub=course_rub_toncoin).apply()
