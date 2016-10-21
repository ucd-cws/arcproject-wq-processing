import os
import wqt_timestamp_match as wqt


def convert_wq_dtypes(df): # TODO check to see if the wq_from_file function can do this
	"""
	Converts all the strings in dataframe into numeric (pd.to_numeric introduced in 0.17 so can't use that)
	:param df:
	:return: dataframe with columns converted to numerics
	"""
	for column in list(df.columns.values):
		if df[column].dtype == object:
			df[column] = df[column].convert_objects(convert_numeric=True)
	return df


def depth_top_meter(wq_vert_profile, depth_field):
	"""
	Selects the rows that within the top 1m of the vertical profile using the depth field
	:param wq_vert_profile: a water quality vertical profile dataframe
	:param depth_field: fieldname that contains the depth information ("DEP25)
	:return: Vertical profile as dataframe that only contains depths within the top 1m of the water surface
	"""

	# Create variable with TRUE if depth is greater than 0 and less than 1
	depth1m = (wq_vert_profile[depth_field] > 0) & (wq_vert_profile[depth_field] < 1)

	# Select all cases where depth1m is TRUE
	wq_1m = wq_vert_profile[depth1m]

	return wq_1m


def avg_vert_profile(vert_profile):
	"""
	Calculates the average water quality values for the water quality columns (must be dtype float) in the profile
	:param vert_profile: water quality vertical profile - only top 1m should be used for the average
	:return: Average values for water quality variables as a dataframe
	"""

	# get the average values of all the rows in the vertical profile
	avg_series = vert_profile.mean() # returns a pandas series

	# convert series to dataframe
	avg_df = avg_series.to_frame().transpose()

	return avg_df


def main(gain_file, site_id, gain_setting):
	"""
	Takes a water quality vertical profile at a specific site, date, and gain setting and returns the average values
	for the top 1m of the water column
	:param gain_file: vertical gain profile
	:param site_id: a unique identifier for the site (two/four letter character string)
	:param gain_setting: the gain setting used when recording the water quality data ("g0", "g1", "g10", "g100")
	:return: pandas dataframe with a single row containing the sample date, site id, gain setting as well as the average
	value for the water quality variables using the top 1m of the vertical profile.
	"""

	# convert raw water quality gain file into pandas dataframe using function from wqt_timestamp_match
	gain_df = wqt.wq_from_file(gain_file)

	# convert data types to float
	num = convert_wq_dtypes(gain_df)  # TODO see if this step could be done in wq_from_file()

	# select the top 1m of the water column
	dep_1m = depth_top_meter(num, "DEP25")

	# average the water quality variables that are in the top meter of the water column
	avg_1m = avg_vert_profile(dep_1m)

	# get start and end sampling datetimes from the original gain dataframe
	start_time = gain_df["Date_Time"][1]  # first row of the data frame
	length = len(gain_df.index)  # total length of the data frame
	end_time = gain_df["Date_Time"][length]  # use length of df because df[-1] doesn't work
	avg_1m['Start_Time'] = start_time  # add start time to the avg df
	avg_1m['End_Time'] = end_time  # add end time to the avg df

	# add site, gain setting information
	avg_1m['Site'] = site_id
	avg_1m['Gain'] = gain_setting

	return avg_1m
