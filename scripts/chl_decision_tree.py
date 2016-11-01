# Decision tree for applying chl correction using linear regression as well as actual values


def chl_decision(uncorrected_chl_value, sample_date):

	# # check if there is a regression for gains?
	#
	# if there is no corrections:
	# 	break
	# elif there is only a gain0 regresion:
	#
	# 	#check the r squared value
	#
	#
	# if uncorrected_chl_value < 5:
	# 	#gain 100
	#
	# elif uncorrected_chl_value < 45:
	# 	#gain 10
	# else:
	# 	#gain 1
	pass


def lookup_regression_values(sample_date, gain_setting):

	rsquared = []
	coeff_a = []
	coeff_b = []

	return [rsquared, coeff_a, coeff_b]
	pass


def chl_correction(uncorreced_chl, a_coeff, b_coeff):
	"""
	Apply the linear regression to the uncorrected chlorophyll value using the intercept and slope from the linear regression
	:param uncorreced_chl: raw chlorophyll value
	:param a_coeff: intercept of the linear regression
	:param b_coeff: slope of the linear regression
	:return: estimated chlorophyll value corrected using the linear regression between lab values and stationary gain
	"""
	corrected_chl_value = a_coeff + b_coeff * uncorreced_chl
	return corrected_chl_value
