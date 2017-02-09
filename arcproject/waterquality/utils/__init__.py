from arcproject.waterquality import classes
import os


def make_tables():
	print("Creating tables")
	classes.Base.metadata.create_all(classes.db_engine)


def recreate_tables():
	try:
		os.remove(classes.db_location)
	except WindowsError:
		print("---------------WARNING-------------------:\n Database not recreated!")
		pass  # likely that the file doesn't exist. Try to create tables now
	make_tables()