from typing import List

from utils.database_api.models.subcategories import Subcategories


class DB_Subcategories:
    async def get_all_subcategories(self, category_id) -> List[Subcategories]:
        return await Subcategories.query.where(Subcategories.category_id == int(category_id)).gino.all()

    async def get_subcategory(self, subcategory_id) -> Subcategories:
        return await Subcategories.query.where(Subcategories.id == int(subcategory_id)).gino.first()
