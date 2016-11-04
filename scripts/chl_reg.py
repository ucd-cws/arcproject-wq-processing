# chl_reg.py
# Chl correction using gain and lab values
import numpy as np


def get_r2_numpy(x, y):
	"""
	http://stackoverflow.com/questions/893657/how-do-i-calculate-r-squared-using-python-and-numpy
	:param x: series for x variable
	:param y: series for y varaible
	:return: rsquared value for linear model fit
	"""
	zx = (x-np.mean(x))/np.std(x, ddof=1)
	zy = (y-np.mean(y))/np.std(y, ddof=1)
	r = np.sum(zx*zy)/(len(x)-1)
	return r**2


def linear_reg_numpy(x, y):
	"""
	linear regression in numpy comparing two series
	:param x: series for x variable
	:param y: series for y variable
	:return: coeffients for linear regression - slope, y-intercept
	"""
	fit = np.polyfit(x, y, 1)
	b_coeff = fit[0]  # slope
	a_coeff = fit[1]  # y-intercept
	return fit



def daily_scatter_plot():
	pass

