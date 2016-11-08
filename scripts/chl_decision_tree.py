# Decision tree for applying chl correction using linear regression as well as actual values

from datetime import datetime

from waterquality import classes

format_string = "%Y-%m-%d"


def load_regression_data(data_frame, field_map=classes.regression_field_map, date_format_string=format_string):

	session = classes.get_new_session()

	try:
		for row in data_frame.itertuples():
			regression = classes.Regression()

			# takes the keys and makes a set to remove unneeded "Index"
			key_set = set(row._asdict().keys())
			key_set.remove("Index")
			keys = list(key_set)

			for key in keys:
				class_field = field_map[key]

				if key == "Date":
					value = datetime.strptime(getattr(row, key), date_format_string)
				else:
					value = getattr(row, key)

				setattr(regression, class_field, value)

			session.add(regression)

		session.commit()
	finally:
		session.close()


def check_gain_reg_exists(session, sample_date, gain_setting, date_format_string=format_string):
	"""
	Given a date and gain setting, check if there exists a regression result in the pandas table that matches
	:param session: a SQLAlchemy database session
	:param sample_date: date to check (should be in format of 'YYYY-MM-DD')
	:param gain_setting: the gain setting to check for
	:return: True or False
	"""
	# Checks if there is a row that matches a given date and gain setting

	has_gain = session.query(classes.Regression)\
					.filter(classes.Regression.date == sample_date,
							classes.Regression.gain == gain_setting)\
					.count() > 0
	return has_gain


def lookup_regression_values(session, sample_date, gain_setting):
	"""
	Return regression values from table given a sample date and gain setting
	:param regression_table_pd: pandas dataframe with the regression results
	:param sample_date: date to check (should be in format of 'YYYY-MM-DD')
	:param gain_setting: gain setting to check (string - g0, g1, g10, g100
	:return: tuple with rsquared value, a coefficient (intercept), b coefficient (slope)
	"""
	record = session.query(classes.Regression) \
		.filter(classes.Regression.date == sample_date,
				classes.Regression.gain == gain_setting)\
		.one()
	return record


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
		print("R-square value {} and significant. Using the lm to correct the chl".format(rsquared))
		corrected_chl = chl_correction(uncorrected_chl_value, a_coeff, b_coeff)
	else:
		print("R-square value {} and not significant. Using uncorrected Chl values".format(rsquared))
		corrected_chl = uncorrected_chl_value

	return corrected_chl


def chl_decision(uncorrected_chl_value, sample_date):
	"""
	Decision tree for correcting Chl values using a linear model regression results
	:param uncorrected_chl_value: the value to correct
	:param regression_table: the table to look up the rsquared, a coeff, b coeff for given date
	:param sample_date: date sample was collected to look up for correction
	:return: corrected chl value if applicable (r square significant for lm)
	"""

	session = classes.get_new_session()

	# gain zero
	if check_gain_reg_exists(session, sample_date, "g0"):
		chl = get_chl_for_gain(session, sample_date, uncorrected_chl_value, gain="g0")
	else:
		if uncorrected_chl_value < 5:
			# use gain 100 regression if significant
			chl = get_chl_for_gain(session, sample_date, uncorrected_chl_value, gain="g100")
		elif uncorrected_chl_value < 45:
			# use gain 100 regression if significant
			chl = get_chl_for_gain(session, sample_date, uncorrected_chl_value, gain="g10")
		else:
			# use gain1 regression if significant
			chl = get_chl_for_gain(session, sample_date, uncorrected_chl_value, gain="g1")

	# TODO there will likely be an error if the regression values don't exist in the table
	# TODO figure out how to catch that. Alternative is to return uncorrected values.

	return chl


def get_chl_for_gain(session, sample_date, uncorrected_chl_value, gain):
	"""

	:param sample_date:
	:param uncorrected_chl_value:
	:param gain:
	:return:
	"""

	reg_values = lookup_regression_values(session, sample_date, gain)
	chl = lm_significant(uncorrected_chl_value, reg_values.r_squared, reg_values.a_coefficient, reg_values.b_coefficient)

	return chl
