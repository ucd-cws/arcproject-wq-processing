import os
import wqt_timestamp_match as wqt
import pandas as pd

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


def gain_join_gps_by_site(gain_avg_df, shp_df):
	"""
	Joins the single row from the avg gain data frame with the coordinates from the shapefile using a common site name
	:param gain_avg_df: mean water quality values for a vertical profile for a single site
	:param shp_df: dataframe from a shapefile of multiple Chl/Zoop sampling sites
	:return: pandas dataframe with the water quality data joined to the GPS attributes
	"""
	# convert both site columns to UPPER
	gain_avg_df['Site'] = gain_avg_df['Site'].str.upper()
	shp_df['Site'] = shp_df['Site'].str.upper()

	# uses inner join to return a dataframe with a single row
	joined = pd.merge(shp_df, gain_avg_df, how="inner", on="Site")

	return joined


def gain_gps_timediff(gain_avg_df, shp_df):
	"""
	Calculates the difference between each of the timestamps in the shapefile and the middle time in the vertical profile
	:param gain_avg_df: mean water quality values for vertical profile (must have start_time and end_time)
	:param shp_df: dataframe from a shapefile of multiple Chl/Zoop sampling sites
	:return: dataframe from shapefile attribute table with a new field storing the absolute time difference
	"""
	# calculate the difference between the start time and the end time of the gain file to get mid point
	mid_time = (gain_avg_df['Start_Time'] + (gain_avg_df['Start_Time'] - gain_avg_df['End_Time']) / 2)[0]

	# for each row of the shapefile df what is the time diffence compared to the mid point?
	shp_df["TimeDelta"] = abs(shp_df["Date_Time"] - mid_time)  # absolute diff of time difference

	return shp_df


def gain_gps_join_closest_timestamp(gain_avg_df, gps_timediff):
	"""
	Joins the average water quality gain dataframe with the closest timestamp from the gps points
	:param gain_avg_df: mean water quality values for vertical profile
	:param gps_timediff: dataframe result from gain_gps_timediff with column TimeDelta
	:return: pandas dataframe with the water quality data joined to the GPS attributes for closest time match
	"""

	# sort by TimeDelta, return the first row (ie the closest match)
	gps_closest_row = gps_timediff.sort('TimeDelta', ascending=True).head(1)

	# join - using concat - the closest match with the water quality average df

	# reset index
	gps_closest_row = gps_closest_row.reset_index(drop=True)
	gain_avg_df = gain_avg_df.reset_index(drop=True)

	join = pd.concat([gps_closest_row, gain_avg_df], axis=1, join='inner')

	# there might be duplicate columns

	return join


def gain_join_logic(gain_avg_df, shp_df):
	"""
	Trys to find a match using the site name, then finds the timestamp with the closest match
	:param gain_avg_df: mean water quality values for vertical profile
	:param shp_df: dataframe from a shapefile of multiple Chl/Zoop sampling sites
	:return:
	"""
	# some logic about how to join the data files together

	# first try to join using the site names
	gain_w_xy = gain_join_gps_by_site(gain_avg_df, shp_df)

	if len(gain_w_xy) != 1:
		print("Matching by site name did not find a match. Joining using the closest timestamp.")
		time_diff = gain_gps_timediff(gain_avg_df, shp_df)
		best_match = gain_gps_join_closest_timestamp(gain_avg_df, time_diff)
		gain_w_xy = best_match

	return gain_w_xy


def main(gain_file, site_id, gain_setting, sample_sites_shp):
	"""
	Takes a water quality vertical profile at a specific site, date, and gain setting and returns the average values
	for the top 1m of the water column
	:param gain_file: vertical gain profile
	:param site_id: a unique identifier for the site (two/four letter character string)
	:param gain_setting: the gain setting used when recording the water quality data ("g0", "g1", "g10", "g100")
	:param sample_sites_shp: shapefile of the sampling sites
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

	# convert shapefile into pandas dataframe using function from wqt_timestamp_match
	sites_shp_df = wqt.wqtshp2pd(sample_sites_shp)

	# join avg_1m with the appropriate attributes from the shp of Zoop/Chl sample points
	joined = gain_join_logic(avg_1m, sites_shp_df)

	return joined
