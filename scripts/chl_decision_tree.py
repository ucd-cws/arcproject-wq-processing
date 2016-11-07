# Decision tree for applying chl correction using linear regression as well as actual values

def check_gain_reg_exists(regression_table_pd, sample_date, gain_setting):
	"""
	Given a date and gain setting, check if there exists a regression result in the pandas table that matches
	:param regression_table_pd: pandas df with the regression results (cols = Date, Gain, Rsquared, A_coeff, B_coeff)
	:param sample_date: date to check (should be in format of 'YYYY-MM-DD')
	:param gain_setting: gain setting to check (string - g0, g1, g10, g100
	:return: True or False
	"""
	# Checks if there is a row that matches a given date and gain setting
	has_gain = ((regression_table_pd['Date'] == sample_date) & (regression_table_pd['Gain'] == gain_setting)).any()
	return has_gain


def lookup_regression_values(regression_table_pd, sample_date, gain_setting):
	"""
	Return regression values from table given a sample date and gain setting
	:param regression_table_pd: pandas dataframe with the regression results
	:param sample_date: date to check (should be in format of 'YYYY-MM-DD')
	:param gain_setting: gain setting to check (string - g0, g1, g10, g100
	:return: tuple with rsquared value, a coefficient (intercept), b coefficient (slope)
	"""
	index = regression_table_pd[(regression_table_pd['Date'] == sample_date) & (regression_table_pd['Gain'] == gain_setting)].index.tolist()

	# select row using the index that matches the sample data and gain setting
	rsquared = regression_table_pd.ix[index, "Rsquared"].values[0]
	coeff_a = regression_table_pd.loc[index, "A_coeff"].values[0]
	coeff_b = regression_table_pd.loc[index, "B_coeff"].values[0]
	return rsquared, coeff_a, coeff_b


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


def chl_decision(uncorrected_chl_value, regression_table, sample_date):
	"""
	Decision tree for correcting Chl values using a linear model regression results
	:param uncorrected_chl_value: the value to correct
	:param regression_table: the table to look up the rsquared, a coeff, b coeff for given date
	:param sample_date: date sample was collected to look up for correction
	:return: corrected chl value if applicable (r square significant for lm)
	"""

	# gain zero
	if check_gain_reg_exists(regression_table, sample_date, "g0"):
		reg_values = lookup_regression_values(regression_table, sample_date, "g0")
		chl = lm_significant(uncorrected_chl_value, reg_values[0], reg_values[1], reg_values[2])

	else:
		if uncorrected_chl_value < 5:
			# use gain 100 regression if significant
			reg_values = lookup_regression_values(regression_table, sample_date, "g100")
			chl = lm_significant(uncorrected_chl_value, reg_values[0], reg_values[1], reg_values[2])

		elif uncorrected_chl_value < 45:
			# use gain 100 regression if significant
			reg_values = lookup_regression_values(regression_table, sample_date, "g10")
			chl = lm_significant(uncorrected_chl_value, reg_values[0], reg_values[1], reg_values[2])

		else:
			# use gain1 regression if significant
			reg_values = lookup_regression_values(regression_table, sample_date, "g1")
			chl = lm_significant(uncorrected_chl_value, reg_values[0], reg_values[1], reg_values[2])

	# TODO there will likely be an error if the regression values don't exist in the table
	# TODO figure out how to catch that. Alternative is to return uncorrected values.

	return chl
