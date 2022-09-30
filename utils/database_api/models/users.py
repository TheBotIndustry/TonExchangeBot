from sqlalchemy import Column, BigInteger, Float, DateTime, Integer, String

from utils.database_api.main import db_gino


class Users(db_gino.Model):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    full_name = Column(String)
    balance_toncoin = Column(Float)
    freeze_balance_toncoin = Column(Float)
    date_registration = Column(DateTime)
    count_deals = Column(Integer)

    def __repr__(self):
        return "<Users(user_id='{}')>".format(self.user_id)
