import datetime

import pandas

from waterquality import classes
from waterquality.classes import WaterQuality as wq


def get_wq_for_date(datetime_object):  # TODO: Add unit tests for this
	"""
	:param datetime_object:
	:return:
	"""
	session = classes.get_new_session()
	try:
		upper_bound = datetime_object.date() + datetime.timedelta(days=1)
		query = session.query(wq).filter(wq.date_time > datetime_object.date(), wq.date_time < upper_bound, wq.x_coord != None, wq.y_coord != None)  # add 1 day's worth of nanoseconds
		return pandas.read_sql(query.statement, query.session.bind)  # get the results as a pandas data frame
	finally:
		session.close()
