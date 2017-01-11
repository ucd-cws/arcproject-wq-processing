import datetime

import pandas

from waterquality import classes
from waterquality.classes import WaterQuality as wq


def get_wq_for_date(datetime_object, shorten_spatial=True, index=False):  # TODO: Add unit tests for this
	"""
	:param datetime_object:
	:return:
	"""
	session = classes.get_new_session()
	try:
		# make a datetime range that's compatible with sqlalchemy/sqlite
		upper_bound = datetime_object.date() + datetime.timedelta(days=1)
		query = session.query(wq).filter(wq.date_time > datetime_object.date(), wq.date_time < upper_bound, wq.x_coord != None, wq.y_coord != None)  # add 1 day's worth of nanoseconds
		df = pandas.read_sql(query.statement, query.session.bind)  # get the results as a pandas data frame

		if shorten_spatial:  # shortens coordinates to 7 places of decimal precision (survey grade for decimal degrees)
			# using Series rounding to support pandas .16.2
			df["x_coord"] = df["x_coord"].round(decimals=7)
			df["y_coord"] = df["y_coord"].round(decimals=7)

		if index:
			# currently seems to not work and removes most columns... don't use
			# make indices for individual columns
			index_columns = ["site_id", "spatial_reference_code", "temp", "ph", "sp_cond", "salinity", "dissolved_oxygen", "dissolved_oxygen_percent", "dep_25", "par", "rpar", "turbidity_sc", "chl", "chl_volts", "chl_corrected", "corrected_gain"]
			if shorten_spatial:
				index_columns += ["x_coord", "y_coord"]

			for col in index_columns:
				df = df.set_index([col])

		return df

	finally:
		session.close()
