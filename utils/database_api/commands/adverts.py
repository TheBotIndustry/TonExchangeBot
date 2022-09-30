import datetime
from typing import List, Dict, Union, Any

from sqlalchemy import and_

from utils.database_api.commands.courses import DB_Courses
from utils.database_api.models.adverts import Adverts
from utils.database_api.models.categories import Categories
from utils.database_api.models.subcategories import Subcategories


class DB_Adverts:
    async def add_advert(self, user_id, cryptocurrency, is_sell, currency, category_id, subCategory_id,
                         limitLow, limitHigh,
                         fixPrice=None, percent=None, decimalPercent=None, comment=None) -> Adverts:
        new_advert = Adverts()
        new_advert.user_id = int(user_id)
        new_advert.cryptocurrency = cryptocurrency
        new_advert.is_sell = is_sell
        new_advert.currency = currency
        new_advert.category_id = int(category_id)
        new_advert.subCategory_id = int(subCategory_id)
        new_advert.limitLow = limitLow
        new_advert.limitHigh = limitHigh
        if fixPrice:
            new_advert.fixPrice = fixPrice
        else:
            new_advert.percent = percent
            new_advert.decimalPercent = decimalPercent
        if comment:
            new_advert.comment = comment
        new_advert.dateCreated = datetime.datetime.utcnow()
        new_advert.status = True
        await new_advert.create()
        return new_advert

    async def get_advert(self, advert_id) -> Adverts:
        return await Adverts.query.where(Adverts.id == int(advert_id)).gino.first()

    async def get_adverts_user(self, user_id, filterMyAdvert) -> List[Adverts]:
        if filterMyAdvert == "All":
            need_list = await Adverts.query.where(Adverts.user_id == int(user_id)).gino.all()
            need_list.sort(key=lambda x: (x.is_sell, x.limitHigh - x.limitLow))
        elif filterMyAdvert == "Buy":
            need_list = await Adverts.query.where(
                and_(Adverts.user_id == int(user_id), Adverts.is_sell == False)).gino.all()
            need_list.sort(key=lambda x: x.limitHigh - x.limitLow)
        else:
            need_list = await Adverts.query.where(
                and_(Adverts.user_id == int(user_id), Adverts.is_sell == True)).gino.all()
            need_list.sort(key=lambda x: x.limitHigh - x.limitLow)
        return need_list

    async def edit_my_advert_course(self, advert_id, fixPrice=None, percent=None, decimalPercent=None):
        advert = await self.get_advert(advert_id)
        if fixPrice:
            await advert.update(fixPrice=fixPrice, percent=None, decimalPercent=None).apply()
        else:
            await advert.update(fixPrice=None, percent=percent, decimalPercent=decimalPercent).apply()

    async def edit_my_advert_limit(self, advert_id, limitLow, limitHigh):
        advert = await self.get_advert(advert_id)
        await advert.update(limitLow=limitLow, limitHigh=limitHigh).apply()

    async def edit_my_advert_comment(self, advert_id, comment):
        advert = await self.get_advert(advert_id)
        await advert.update(comment=comment).apply()

    async def delete_advert(self, advert_id):
        advert = await self.get_advert(advert_id)
        await advert.delete()

    async def get_categories_market(self, market_is_sell, currency, cryptocurrency) -> Dict[Categories, int]:
        adverts = await Adverts.query.where(and_(Adverts.is_sell != market_is_sell, Adverts.currency == currency,
                                                 Adverts.cryptocurrency == cryptocurrency,
                                                 Adverts.status == True)).gino.all()
        categories_list = []
        for advert in adverts:
            categories_list.append(advert.category_id)
        return dict((x, categories_list.count(x)) for x in set(categories_list))

    async def get_subcategories_market(self, market_is_sell, currency, category_id, cryptocurrency) -> Dict[
        Subcategories, int]:
        adverts = await Adverts.query.where(and_(Adverts.is_sell != market_is_sell, Adverts.currency == currency,
                                                 Adverts.category_id == int(category_id),
                                                 Adverts.cryptocurrency == cryptocurrency,
                                                 Adverts.status == True)).gino.all()
        subcategories_list = []
        for advert in adverts:
            subcategories_list.append(advert.subCategory_id)
        return dict((x, subcategories_list.count(x)) for x in set(subcategories_list))

    async def get_adverts_market(self, market_is_sell, currency,
                                 subcategory_id, cryptocurrency) -> List[Union[Dict[str, Any], Dict[str, Any]]]:
        adverts = await Adverts.query.where(and_(Adverts.is_sell != market_is_sell, Adverts.currency == currency,
                                                 Adverts.subCategory_id == int(subcategory_id),
                                                 Adverts.cryptocurrency == cryptocurrency,
                                                 Adverts.status == True)).gino.all()
        course = await DB_Courses().get_course(cryptocurrency)
        course_price = 1
        if currency == "USD":
            course_price = course.course
        elif currency == "RUB":
            course_price = course.course_rub
        list_adverts_dict = []
        for advert in adverts:
            if advert.fixPrice:
                list_adverts_dict.append({"advert": advert, "price": advert.fixPrice})
            else:
                advert_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
                list_adverts_dict.append({"advert": advert, "price": round(course_price / 100 * advert_percent, 2)})
        if market_is_sell:
            list_adverts_dict.sort(key=lambda x: x['price'], reverse=True)
        else:
            list_adverts_dict.sort(key=lambda x: x['price'])
        return list_adverts_dict

    async def get_adverts_filter_market(self, market_is_sell, currency,
                                        subcategory_id, cryptocurrency, filter_parameter, amount_parameter) -> List[
        Union[Dict[str, Any], Dict[str, Any]]]:
        adverts = await Adverts.query.where(and_(Adverts.is_sell != market_is_sell, Adverts.currency == currency,
                                                 Adverts.subCategory_id == int(subcategory_id),
                                                 Adverts.cryptocurrency == cryptocurrency,
                                                 Adverts.status == True)).gino.all()
        course = await DB_Courses().get_course(cryptocurrency)
        course_price = 1
        if currency == "USD":
            course_price = course.course
        elif currency == "RUB":
            course_price = course.course_rub
        list_adverts_dict = []
        for advert in adverts:
            if advert.fixPrice:
                if filter_parameter == cryptocurrency:
                    if advert.limitHigh >= amount_parameter >= advert.limitLow:
                        list_adverts_dict.append({"advert": advert, "price": advert.fixPrice})
                else:
                    if advert.limitHigh * advert.fixPrice >= amount_parameter >= advert.limitLow * advert.fixPrice:
                        list_adverts_dict.append({"advert": advert, "price": advert.fixPrice})
            else:
                if filter_parameter == cryptocurrency:
                    if advert.limitHigh >= amount_parameter >= advert.limitLow:
                        advert_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
                        list_adverts_dict.append(
                            {"advert": advert, "price": round(course_price / 100 * advert_percent, 2)})
                else:
                    if advert.limitHigh * course_price >= amount_parameter >= advert.limitLow * course_price:
                        advert_percent = 100 + advert.percent if advert.decimalPercent == "+" else 100 - advert.percent
                        list_adverts_dict.append(
                            {"advert": advert, "price": round(course_price / 100 * advert_percent, 2)})
        if market_is_sell:
            list_adverts_dict.sort(key=lambda x: x['price'], reverse=True)
        else:
            list_adverts_dict.sort(key=lambda x: x['price'])
        return list_adverts_dict

    async def advert_change_status(self, advert_id):
        advert = await self.get_advert(advert_id)
        if advert.status:
            await advert.update(status=False).apply()
        else:
            await advert.update(status=True).apply()
