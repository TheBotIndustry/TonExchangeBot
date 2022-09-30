from sqlalchemy import Column, Float, Integer, String

from utils.database_api.main import db_gino


class Courses(db_gino.Model):
    __tablename__ = "courses"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String)
    course = Column(Float)
    course_rub = Column(Float)

    def __repr__(self):
        return "<Courses(id='{}')>".format(self.id)
