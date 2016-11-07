# chl_reg.py
# Chl correction using gain and lab values
import os
import numpy as np
import matplotlib.pyplot as plt


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


def subset_wqt_by_gain(avg_wq_site_df, gain_field_name, gain_setting):
	"""
	Subsets daily water quality by specified gain setting
	:param avg_wq_site_df: average vertical profiles by site for specific date
	:param gain_field_name: field name that stores the gain settings
	:param gain_setting: gain setting (gn0, gn1, gn10, gn100)
	:return: water quality subseted by gain
	"""
	subset = avg_wq_site_df[avg_wq_site_df[gain_field_name] == gain_setting]
	return subset


def join_field_w_lab(wq_single_gain, chl_lab_single_date, wq_site_fieldname, lab_site_fieldname):
	"""
	Joins lab data to a single gain for a single date
	:param chl_lab_single_date: all the lab values for a single sampling date
	:param wq_site_fieldname: the name of the field storing the siteid in the gain file to join on
	:param lab_site_fieldname: the name of the field storing the siteid in the lab file to join on
	:return: dataframe with lab values joined by site to the appropriate field measurement
	"""
	join_lab = wq_single_gain.merge(chl_lab_single_date, left_on=wq_site_fieldname,
	                                right_on=lab_site_fieldname, suffixes=('', '_y'))
	return join_lab


def chl_field_lab_series(df_with_field_plus_lab, field_chl, lab_chl, sites):
	"""
	Picks out chl columns to use in regression
	:param df_with_field_plus_lab: result from join_field_w_lab
	:param field_chl: fieldname of column storing Chl values from the field
	:param lab_chl: fieldname of column storing Chl values from the lab
	:param sites: fieldname of column storing sitenames
	return:
	"""
	x = df_with_field_plus_lab[field_chl] # field
	y = df_with_field_plus_lab[lab_chl] # lab
	s = df_with_field_plus_lab[sites] # sites
	return x,y,s


def chl_daily_scatter(field_chl, lab_chl, date=None, gain=None, output_location=None, siteid=None):
	"""
	Creates scatterplot showing the regression between field values and lab values for chl
	:param field_chl: series with chl measured in the field
	:param lab_chl: series with chl measured in the lab
	:param date: sample date to use in title
	:param gain: gain setting to use in title
	:param output_location: location to save scatter plot (filename will be {date}_{gain}.png
	:param siteid: Optional series with siteid to show on the plot
	:return:
	"""
	x = field_chl
	y = lab_chl

	fit = linear_reg_numpy(x, y)
	b_coeff = fit[0]  # slope
	a_coeff = fit[1]  # y-intercept

	# fit_fn is now a function which takes in x and returns an estimate for y
	fit_fn = np.poly1d(fit)

	# r squared fit
	rsquared = get_r2_numpy(x, y)

	plt.plot(x, y, 'bo')  # plot the points
	plt.plot(x, fit_fn(x), '--')
	plt.margins(x=0.1, y=0.1)
	plt.ylabel("Lab Chl")
	plt.xlabel("Field Chl")

	plt.annotate("$R^{2}=$" + str(round(rsquared, 4)), xy=(0.05, 0.9), xycoords='axes fraction',
	             fontsize=8)
	plt.annotate("$y=$" + str(round(b_coeff, 2)) + "x + " + str(round(a_coeff, 2)), xy=(0.05, 0.85),
	             xycoords='axes fraction',
	             fontsize=8)

	if not siteid.empty:
		for i, txt in enumerate(siteid):
			plt.annotate(txt, (x[i], y[i]), xytext=(0, 5), textcoords='offset points', horizontalalignment='center',
			             verticalalignment='bottom')

	if date and gain is not None:
		plt.title(date + " " + gain)

	if output_location is not None:
		plt.savefig(os.path.join(output_location, date + "_" + gain + ".png"))
	plt.show()
	plt.close()
	return plt


def subset_gain_table_by_single_day():
	# TODO - get the average wq values for all gains for a single day
	pass


def subset_lab_by_single_day():
	# TODO - get the lab water quality values for a single day
	pass


def main(single_day_gain_avg, lab_values_single_day, gain_setting, view_scatter=None):
	"""
	For a given gain setting, run regression between field chl values and lab values
	:param single_day_gain_avg: summary of wq avg from vertical profile by site
	:param lab_values_single_day: all lab values for given day
	:param gain_setting: gain to run regression on
	:param date: date of regression only used for scatterplot
	:param save_scatter: optional - location to save scatter plot
	:return: rsquared, a_coefficient, b_coefficient
	"""

	# TODO allow user to select day

	# subset the gain summary file (average of top 1m water column for every site) by the selected gain
	gain_subset = subset_wqt_by_gain(single_day_gain_avg, "Gain", gain_setting)

	# join the results from the lab
	join_lab = join_field_w_lab(gain_subset, lab_values_single_day, "Site", "SiteID")

	# pull out the chl columns and siteids for the regression
	chl_data_series = chl_field_lab_series(join_lab, "Chl", "ChlA", "Site")

	# linear regression using between the two types of chl measurements
	lm = linear_reg_numpy(chl_data_series[0], chl_data_series[1])
	b_coeff = lm[0]  # slope
	a_coeff = lm[1]  # y-intercept
	rsquared = get_r2_numpy(chl_data_series[0], chl_data_series[1])  # rsquared

	# save scatter plot
	if view_scatter is True:
		chl_daily_scatter(chl_data_series[0], chl_data_series[1], gain=gain_setting, siteid=chl_data_series[2])

	return rsquared, a_coeff, b_coeff

