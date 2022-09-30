from sqlalchemy import Column, Float, Integer, String, BigInteger, Boolean, DateTime

from utils.database_api.main import db_gino


class Deal(db_gino.Model):
    __tablename__ = "deal"

    id = Column(Integer, autoincrement=True, primary_key=True)
    category_id = Column(Integer)
    subcategory_id = Column(Integer)
    advert_id = Column(Integer)
    creator_user_id = Column(BigInteger)
    user_id = Column(BigInteger)
    is_sell = Column(Boolean)
    is_deposit_for_sell = Column(Boolean)
    cryptocurrency = Column(String)
    currency = Column(String)
    amount_crypto = Column(Float)
    amount_currency = Column(Float)
    status_start = Column(Boolean)
    payment = Column(String)
    status_finish = Column(Boolean)
    status_arbitr = Column(Boolean)
    date_start = Column(DateTime)
    date_finish = Column(DateTime)
    creator_mess_id = Column(Integer)
    user_mess_id = Column(Integer)

    def __repr__(self):
        return "<Deal(id='{}')>".format(self.id)
