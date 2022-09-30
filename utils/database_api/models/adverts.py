from sqlalchemy import Column, BigInteger, Float, DateTime, Integer, String, Boolean

from utils.database_api.main import db_gino


class Adverts(db_gino.Model):
    __tablename__ = "adverts"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    cryptocurrency = Column(String)
    is_sell = Column(Boolean)
    currency = Column(String)
    category_id = Column(Integer)
    subCategory_id = Column(Integer)
    fixPrice = Column(Float)
    percent = Column(Float)
    decimalPercent = Column(String)
    comment = Column(String)
    dateCreated = Column(DateTime)
    limitLow = Column(Float)
    limitHigh = Column(Float)
    status = Column(Boolean)

    def __repr__(self):
        return "<Adverts(id='{}')>".format(self.id)
