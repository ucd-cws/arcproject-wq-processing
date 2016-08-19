import os

import sqlalchemy
from sqlalchemy import orm

db_name = "wqdb.sqlite"
db_location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), db_name)
db_engine = None


def connect_db(database=db_location):
	"""
		Just a helper function that sets up the database engine
	:return:
	"""
	global db_engine
	db_engine = sqlalchemy.create_engine('sqlite:///{}'.format(database))


def db_session(engine=db_engine):
	"""
		provides a Session to the database - can be run for each thing that needs a new session.
	:param engine:
	:return:
	"""
	return orm.sessionmaker(bind=engine)