# Decision tree for applying chl correction using linear regression as well as actual values
import pandas as pd
import os

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





# set wd to Arcproject-wq-processing folder
# wd = os.path.abspath((os.path.join(os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(os.path.dirname("__file__"))))))))
# regression_table = os.path.join(wd, r"data\legacy\lm_coeffs_rsquared\legacy_coeffs_rsquared.csv")
# regression_table = pd.read_csv(regression_table)
# print(regression_table.head())
# print(regression_table.head().to_records())


def check_gain_reg_exists(regression_table_pd, sample_date, gain_setting):
	# this should return True or False
	has_gain = ((regression_table_pd['Date'] == sample_date) & (regression_table_pd['Gain'] == gain_setting)).any()
	return has_gain


def lookup_regression_values(regression_table_pd, sample_date, gain_setting):
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
