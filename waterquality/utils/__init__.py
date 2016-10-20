from .. import classes
import os


def make_tables():
	print("Creating tables")
	classes.connect_db(classes.db_location)
	classes.Base.metadata.create_all(classes.db_engine)


def recreate_tables():
	os.remove(classes.db_location)
	make_tables()