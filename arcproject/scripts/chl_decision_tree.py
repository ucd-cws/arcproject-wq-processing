# Decision tree for applying chl correction using linear regression as well as actual values

from datetime import datetime
import six
import numpy
import pandas
from .. import waterquality
from ..waterquality.utils import shorten_float
from sqlalchemy import exc

classes = waterquality.classes

format_string = "%Y-%m-%d"


def load_data_from_csv(csv_path, field_map=classes.regression_field_map, date_format_string=format_string, table_class=classes.Regression):
	"""
		Given the path to a CSV file containing regression values, loads them to the database. Takes a field map to translate
		table CSV fields to the DB. Loads the CSV to a Pandas data frame, then calls load_regression_data
	:param csv_path: Path to CSV with values to load
	:param field_map: Field map that translates those values to the database fields
	:param date_format_string: The format string to use when translating dates to machine dates
	:param table_class: the class type of this table
	:return: None
	"""

	load_df_data(pandas.read_csv(csv_path), field_map=field_map, date_format_string=date_format_string, table_class=table_class)


def load_df_data(data_frame, field_map=classes.regression_field_map, date_format_string=format_string, table_class=classes.Regression):
	"""
		Given a pandas data frame containing regression values, loads them to the database. Takes a field map to translate
		table CSV fields to the DB.
	:param data_frame: The pandas data frame to load into the Regression table
	:param field_map: Field map that translates those values to the database fields
	:param date_format_string: The format string to use when translating dates to machine dates
	:param table_class: the class type of this table
	:return: None
	"""

	session = classes.get_new_session()

	try:
		for row in data_frame.iterrows():
			regression = table_class()

			# row[1] is the actual data that is included in the row
			row1 = row[1]

			for key in row1.index:
				class_field = field_map[key]
				if key == "Date" or key == "Date_Time":
					value = datetime.strptime(getattr(row1, key), date_format_string)
				else:
					value = getattr(row1, key)

				if type(value) in (float, numpy.float64):  # shorten any floating point number to 8 places for consistency
					value = shorten_float(value)

				setattr(regression, class_field, value)

			session.add(regression)
			try:  # committing here instead of in a batch so that if we have a mix of new and old, the new values get committed
				session.commit()
			except exc.IntegrityError as e:
				session.rollback()  # need to rollback so can proceed, but it's fine to have this error - means row already exists

	finally:
		session.close()


def pullRegresionTable(session):
	"""
	Creates query to pull records from the regression table
	:param session: an open SQLAlchemy database session
	:return: a list of regression objects
	"""
	# pull all the data from the regression table in a single query
	# this avoids calling this for every records which spawns thousands of queries in the loop
	reg = classes.Regression
	reg_table = session.query(reg).all()
	return reg_table


def RegListComp(list_reg_obj, date, gain):
	"""
	Filters the regression table objects by a specific date and gain setting
	:param list_reg_obj: a list objects of type regression class
	:param date: desired date as a python date time object
	:param gain: desired gain setting
	:return: regression object
	"""
	# gets the date only from the python date time object
	date = date.date()
	# use list comprehension to filter all elements with desired gain setting and date
	subset = [x for x in list_reg_obj if (x.date == date and x.gain == gain)]

	if len(subset) == 1:
		reg = subset[0]

	elif len(subset) == 0:
		# regression does not exist
		# need to do something with this use case
		raise Exception("Regression values does not exist for this date and gain setting!")
	else:
		raise Exception("Regression values for date and gain must be unique!")
	return reg


def chl_correction(uncorrected_chl, a_coeff, b_coeff):
	"""
	Apply the linear regression to the uncorrected chlorophyll value using the intercept and slope from the linear regression
	:param uncorrected_chl: raw chlorophyll value
	:param a_coeff: intercept of the linear regression
	:param b_coeff: slope of the linear regression
	:return: estimated chlorophyll value corrected using the linear regression between lab values and stationary gain
	"""
	corrected_chl_value = a_coeff + b_coeff * uncorrected_chl
	return corrected_chl_value


def lm_significant(uncorrected_chl_value, rsquared, a_coeff, b_coeff):
	"""
	Determines if lm regression is significant (rsquared>0.8) and if so corrects chl using lm. If not returns
	the original value of chl uncorrected
	:param uncorrected_chl_value:
	:param rsquared: r squared value of the linear model
	:param a_coeff: intercept of linear model to correct chl
	:param b_coeff: slope linear model to correct chl
	:return: corrected chl
	"""
	if rsquared > 0.8:
		corrected_chl = chl_correction(uncorrected_chl_value, a_coeff, b_coeff)
	else:
		corrected_chl = uncorrected_chl_value
	return corrected_chl


def check_gain_reg_exists(regression_table, sample_date, gain):
	"""
	Checks if a there are values in the regression table for specific date and gain setting
	:param regression_table:
	:param sample_date:
	:param gain:
	:return: Boolean
	"""
	try:
		t = RegListComp(regression_table, sample_date, gain)
		return True
	except:
		return False


def get_chl_for_gain(uncorrected_chl_value, list_reg_obj, sample_date, gain):
	"""
	For specific date and gain, applies the linear model to an uncorrected chl value
	:param uncorrected_chl_value: raw chl value
	:param list_reg_obj: output of pullRegresionTable (ie a list of regression objects)
	:param sample_date: python date time object for date uncorrect chl was measured
	:param gain: get setting to use for the lm lookup
	:return: corrected chl value based on the lm of the specified gain if the lm is significant
	"""
	reg_values = RegListComp(list_reg_obj, sample_date, gain)
	chl = lm_significant(uncorrected_chl_value, reg_values.r_squared, reg_values.a_coefficient, reg_values.b_coefficient)
	return chl


def chl_decision(uncorrected_chl_value, regression_table, sample_date):
	"""
	Decision tree for correcting Chl values using a linear model regression results
	:param uncorrected_chl_value: the value to correct
	:param regression_table: the table to look up the rsquared, a coeff, b coeff for given date
	:param sample_date: date sample was collected to look up for correction
	:return: corrected chl value if applicable (r square significant for lm)
	"""
	# gain zero
	if check_gain_reg_exists(regression_table, sample_date, 0):
		chl = get_chl_for_gain(uncorrected_chl_value, regression_table, sample_date, gain=0)
	else:
		if uncorrected_chl_value < 5 and check_gain_reg_exists(regression_table, sample_date, 100):
			# use gain 100 regression if significant
			chl = get_chl_for_gain(uncorrected_chl_value, regression_table, sample_date, gain=100)
		elif uncorrected_chl_value < 45 and check_gain_reg_exists(regression_table, sample_date, 10):
			# use gain 10 regression if significant
			chl = get_chl_for_gain(uncorrected_chl_value, regression_table, sample_date, gain=10)
		elif check_gain_reg_exists(regression_table, sample_date, 1):
			# use gain1 regression if significant
			chl = get_chl_for_gain(uncorrected_chl_value, regression_table, sample_date, gain=1)
		else:
			#print("Unable to correct CHL since regression values don't exist in the table.")
			#print("Returning uncorrected values")
			chl = None
	return chl


def queryBuilder(session, query_type="NEW", idrange=None, dates=None):
	"""
	Creates query to pull records from water quality table
	:param session: an open SQLAlchemy database session
	:param query_type: choose "ALL", "NEW", "IDRANGE", or "DATERANGE"
	:param idrange: when query_type="IDRANGE" range of ids as list where [start_id, end_id]
		Ex: main(session, "RANGE", idrange=[120, 2000])
	:param dates: when query_type="DATERANGE" two datetime objects as list where [start_date, end_date].
		Ex: main(session, "DATERANGE",  dates=[datetime.datetime(2016, 1, 01), datetime.datetime(2016, 1, 31)])
	:return: a SQLAlchemy query object
	"""
	wq = classes.WaterQuality

	if query_type == "ALL":
		# update all records in wq table
		q = session.query(wq).filter(wq.chl != None)  # all records that have chl values
	elif query_type == "NEW":
		q = session.query(wq).filter(wq.chl != None, wq.chl_corrected == None)
	elif query_type == "IDRANGE" and idrange is not None:
		q = session.query(wq).filter(wq.id >= idrange[0], wq.id <= idrange[1], wq.chl != None)
	elif query_type == "DATERANGE" and dates is not None:
		upper_bound = dates[1] + datetime.timedelta(days=1)
		q = session.query(wq).filter(wq.date_time > dates[0], wq.date_time < upper_bound, wq.chl != None)
	else:
		raise Exception("Input params are not valid.")
	return q


def main(query_type="NEW", daterange=None, idrange=None):
	"""
	Updates the water quality table corrected CHL by applying the linear regression values from the regression table
	:param query_type: Subset of records to run update on ("ALL", "NEW", "DATERANGE", "IDRANGE"
	:param idrange: when query_type="IDRANGE" range of ids as list where [start_id, end_id]
		Ex: main(session, "RANGE", idrange=[120, 2000])
	:param daterange: when query_type="DATERANGE" two datetime objects as list where [start_date, end_date].
		Ex: main(session, "DATERANGE",  dates=[datetime.datetime(2016, 1, 01), datetime.datetime(2016, 1, 31)])
	:return:
	"""
	session = classes.get_new_session()
	query = queryBuilder(session, query_type, idrange, daterange)
	reg_table = pullRegresionTable(session)
	try:
		# iterate over each row
		print(query.count())

		for row in query:
			# get the date only from the date_time field
			dt = row.date_time

			# decision tree using date and uncorrected chl value
			updated_chl = chl_decision(row.chl, reg_table, dt)
			row.chl_corrected = updated_chl

		# commit session
		session.commit()
	except Exception as e:
		print(e)
		pass
	session.close()
	return

if __name__ == '__main__':
	main(query_type="NEW")
