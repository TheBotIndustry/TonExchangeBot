from utils.database_api.commands.adverts import DB_Adverts
from utils.database_api.commands.categories import DB_Categories
from utils.database_api.commands.courses import DB_Courses
from utils.database_api.commands.deal import DB_Deal
from utils.database_api.commands.subcategories import DB_Subcategories
from utils.database_api.commands.users import DB_Users


class DB_Commands(DB_Users, DB_Courses, DB_Adverts, DB_Categories, DB_Subcategories, DB_Deal):
    pass
