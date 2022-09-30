from sqlalchemy import Column, Integer, String

from utils.database_api.main import db_gino


class Categories(db_gino.Model):
    __tablename__ = "categories"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    currency = Column(String)

    def __repr__(self):
        return "<Categories(id='{}')>".format(self.id)
