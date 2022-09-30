from sqlalchemy import Column, Integer, String

from utils.database_api.main import db_gino


class Subcategories(db_gino.Model):
    __tablename__ = "subcategories"

    id = Column(Integer, autoincrement=True, primary_key=True)
    category_id = Column(Integer)
    name = Column(String)

    def __repr__(self):
        return "<Subcategories(id='{}')>".format(self.id)
