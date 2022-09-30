from typing import List

from utils.database_api.models.categories import Categories


class DB_Categories:
    async def get_all_categories(self, currency) -> List[Categories]:
        return await Categories.query.where(Categories.currency == currency).gino.all()

    async def get_category(self, category_id) -> Categories:
        return await Categories.query.where(Categories.id == int(category_id)).gino.first()
