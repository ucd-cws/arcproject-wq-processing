from .. import classes


def make_tables():
	print("Creating tables")
	classes.connect_db(classes.db_location)
	classes.Base.metadata.create_all(classes.db_engine)