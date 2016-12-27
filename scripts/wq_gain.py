from scripts import wqt_timestamp_match as wqt
import pandas as pd
from waterquality import classes
import logging
import traceback
import six
from string import digits
import os


def convert_wq_dtypes(df):  # TODO check to see if the wq_from_file function can do this
	"""
	Converts all the strings in dataframe into numeric (pd.to_numeric introduced in 0.17 so can't use that)
	:param df:
	:return: dataframe with columns converted to numeric
	"""
	for column in list(df.columns.values):
		if df[column].dtype == object:
			if pd.__version__ >= "0.17":  # separate ways to convert to numeric before and after version 0.17
				try:
					df[column] = pd.to_numeric(df[column])
				except ValueError:  # try coercing the numeric fields - if it an exception is raised, we should be able to continue becuase we just need to numbers to act like numbers - it's ok if text stays text
					pass
			else:
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
	avg_series = vert_profile.mean()  # returns a pandas series

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


def gain_gps_timediff(gain_avg_df):
	"""
	Calculates the difference between each of the timestamps in the shapefile and the middle time in the vertical profile
	:param gain_avg_df: mean water quality values for vertical profile (must have start_time and end_time)
	:param shp_df: dataframe from a shapefile of multiple Chl/Zoop sampling sites
	:return: dataframe from shapefile attribute table with a new field storing the absolute time difference
	"""
	# calculate the difference between the start time and the end time of the gain file to get mid point
	mid_time = (gain_avg_df['Start_Time'] + (gain_avg_df['Start_Time'] - gain_avg_df['End_Time']) / 2)[0]

	# for each row of the shapefile df what is the time difference compared to the mid point?
	gain_avg_df["TimeDelta"] = abs(gain_avg_df["Date_Time"] - mid_time)  # absolute diff of time difference

	return gain_avg_df


def profile_function_historic(*args, **kwargs):
	"""
	Site functions are passed to wq_df2database so that it can determine which site a record is from. Historic data
	will use this function since it will parse if off the data frame as constructed in this code (which includes
	a field for the filename, which has the site code). Future data will have another method and use a different site
	function that will be passed to wq_df2database

	:param args:
	:param kwargs:
	:return: site object
	"""
	part = kwargs["part"]
	filename = kwargs["filename"]  # get the value of the data source field (source_field defined globally)
	try:
		part_code = filename.split("_")[int(part)].upper()  # get the selected underscored part of the name
	except IndexError:
		raise IndexError("Filename was unable to be split based on underscore in order to parse site name -"
		                 " be sure your filename format matches the site function used, or that you're using "
		                 "the correct site retrieval function")
	return part_code


def gain_wq_df2database(data, field_map=classes.gain_water_quality_header_map, session=None):
	"""
	Given a pandas data frame of water quality records, translates those records to ORM-mapped objects in the database.

	:param data: a pandas data frame of water quality records
	:param field_map: a field map (dictionary) that translates keys in the data frame (as the dict keys) to the keys used
		in the ORM - uses a default, but when the schema of the data files is different, a new field map will be necessary
	:param session: a SQLAlchemy session to use - for tests, we often want the session passed so it can be inspected,
		otherwise, we'll likely just create it. If a session is passed, this function will NOT commit new records - that
		becomes the responsibility of the caller.
	:return:
	"""

	if not session:  # if no session was passed, create our own
		session = classes.get_new_session()
		session_created = True
	else:
		session_created = False

	try:
		records = data.iterrows()
		for row in records:  # iterates over all of the rows in the data frames the fast way
			gain_make_record(field_map, row[1], session)  # row[1] is the actual data included in the row
		if session_created:  # only commit if this function created the session - otherwise leave it to caller
			session.commit()  # saves all new objects
	finally:
		if session_created:
			session.close()


def gain_make_record(field_map, row, session):
	"""
	Called for each record in the loaded and joined Pandas data frame. Given a named tuple of a row in the data frame,
	 translates it into a waterquality object
	:param field_map: A field map dictionary with keys based on the data frame fields and values of the database field
	:param row: a named tuple of the row in the data frame to translate into the WaterQuality object
	:param session: an open SQLAlchemy database session
	:return:
	"""

	profile = classes.VerticalProfile()  # instantiates a new object

	for key in row.index:  # converts named_tuple to a Dict-like and gets the keys
		# look up the field that is used in the ORM/database using the key from the namedtuple.
		try:
			class_field = field_map[key]
		except KeyError:
			# logging.warning("Skipping field {} with value {}. Field not found in field map.".format(key, getattr(row, key)))
			continue

		if class_field is None:  # if it's an explicitly defined None and not nonexistent, then skip it silently
			continue

		try:
			setattr(profile, class_field, getattr(row, key))  # for each value, it sets the object's value to match
		except AttributeError:
			print("Incorrect field map - original message was {}".format(traceback.format_exc()))

	else:  # if we don't break for a bad site code or something else, then add the object
		session.add(profile)  # adds the object for creation in the DB - will be committed later.
	return


def main(gain_file, site=profile_function_historic, gain=profile_function_historic, sample_sites_shp=None,
         site_gain_params=wqt.site_function_params):
	"""
	Takes a water quality vertical profile at a specific site, date, and gain setting and returns the average values
	for the top 1m of the water column
	:param gain_file: vertical gain profile
	:param site: a unique identifier for the site (2-4 letter character string) or a function to parse the profile name
	:param gain: the gain setting used when recording the water quality data ("0", "1", "10", "100") or a function to
	parse the gain setting
	:param sample_sites_shp: OPTIONAL shapefile with field called "Site" to add XY coords to gain sample
	:param site_gain_params: parameters to pass to the site function
	:return:
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

	# add source of wqp file (get's lost when the file gets averaged)
	wqt.addsourcefield(avg_1m, "WQ_SOURCE", gain_file)

	# basename of the source gain file
	base = os.path.basename(gain_file)
	print(base)
	# try parsing the site from the filename
	try:
		# If it's a text code, use the text, otherwise call the function
		if isinstance(site, six.string_types):
			avg_1m['Site'] = site.upper()
		else:
			avg_1m['Site'] = site(filename=base, part=site_gain_params["site_part"])
	except ValueError:
		traceback.print_exc()

	# try parsing the gain setting from the filename
	try:
		# If gain setting the gain is provided use it, otherwise call the function
		if isinstance(gain, six.integer_types) or isinstance(gain, six.string_types):
			# strip all letters from gain setting ("GN10" -> 10)
			digits_only = ''.join(c for c in str(gain) if c in digits)
			gain_digits = int(digits_only)
			avg_1m['Gain'] = gain_digits
		else:
			gain_setting_from_name = gain(filename=base, part=site_gain_params["gain_part"])
			digits_only = ''.join(c for c in str(gain_setting_from_name) if c in digits)
			gain_digits = int(digits_only)
			avg_1m['Gain'] = gain_digits

	except ValueError:
		traceback.print_exc()

	# strip out any characters in the gain file (ie "gn1" becomes "1")


	# if shapefile provided try joining using the site field
	if sample_sites_shp is not None:
		if isinstance(sample_sites_shp, list):
			sites_shp_df = wqt.gps_append_fromlist(sample_sites_shp)
		elif isinstance(sample_sites_shp, pd.DataFrame):
			sites_shp_df = sample_sites_shp
		else:
			# convert shapefile into pandas dataframe using function from wqt_timestamp_match
			sites_shp_df = wqt.wqtshp2pd(sample_sites_shp)

		# join using the site names from an attribute field
		gain_w_xy = gain_join_gps_by_site(avg_1m, sites_shp_df)

		# check that there is data in the join
		if gain_w_xy.size == 0:
			logging.warning("Unable to add XY coords. Make sure GPS file has {} as an attribute in Site field".format(site))
		elif gain_w_xy.shape[0] != 1:
			logging.warning("Multiple rows in the shapefile match the site code. Matching based on closest time stamp")

			# calculate time diff for all rows
			gps_timediff = gain_gps_timediff(gain_w_xy)
			gps_closest_row = gps_timediff.sort('TimeDelta', ascending=True).head(1)
			avg_1m = gps_closest_row
		else:
			avg_1m = gain_w_xy

	# add row to database table vertical_profiles
	gain_wq_df2database(avg_1m)

	return
