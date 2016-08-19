import os

import sqlalchemy
from sqlalchemy import orm

db_name = "wqdb.sqlite"
db_location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_name)
db_engine = None


def connect_db():
	global db_engine
	db_engine = sqlalchemy.create_engine('sqlite:///{}'.format(db_location))


def db_session(engine=db_engine):
	return orm.sessionmaker(bind=engine)