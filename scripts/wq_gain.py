from scripts import wqt_timestamp_match as wqt
import pandas as pd
from waterquality import classes
from waterquality import utils
import logging
import traceback
from sqlalchemy import exc
import six

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
		# this isn't the fastest approach in the world, but it will create objects for each data frame record in the database.
		for row in records:  # iterates over all of the rows in the data frames the fast way
			gain_make_record(field_map, row[1], session) # row[1] is the actual data included in the row
		if session_created:  # only commit if this function created the session - otherwise leave it to caller
			session.commit()  # saves all new objects
	finally:
		if session_created:
			session.close()


def gain_make_record(field_map, row, session):
	"""
	 	Called for each record in the loaded and joined Pandas data frame. Given a named tuple of a row in the data frame, translates it into a waterquality object
	:param field_map: A field map dictionary with keys based on the data frame fields and values of the corresponding database field
	:param row: a named tuple of the row in the data frame to translate into the WaterQuality object
	:param session: an open SQLAlchemy database session
	:return:
	"""

	profile = classes.VerticalProfile()  # instantiates a new object

	for key in row.index:  # converts named_tuple to a Dict-like and gets the keys
		# look up the field that is used in the ORM/database using the key from the namedtuple. If it doesn't exist, throw a warning and move on to next field
		try:
			class_field = field_map[key]
		except KeyError:
			logging.warning("Skipping field {} with value {}. Field not found in field map.".format(key, getattr(row, key)))
			continue

		if class_field is None:  # if it's an explicitly defined None and not nonexistent (handled in above exception), then skip it silently
			continue

		try:
			setattr(profile, class_field, getattr(row, key))  # for each value, it sets the object's value to match
		except AttributeError:
			print("Incorrect field map - original message was {}".format(traceback.format_exc()))

	else:  # if we don't break for a bad site code or something else, then add the object
		session.add(profile)  # and adds the object for creation in the DB - will be committed later before the session is closed.
	return


def main(gain_file, site, gain, sample_sites_shp=None):
	"""
	Takes a water quality vertical profile at a specific site, date, and gain setting and returns the average values
	for the top 1m of the water column
	:param gain_file: vertical gain profile
	:param site: a unique identifier for the site (two/four letter character string)
	:param gain: the gain setting used when recording the water quality data ("0", "1", "10", "100")
	:param sample_sites_shp: OPTIONAL shapefile with field called "Site" to add XY coords to gain sample
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

	# add source of wqp file (get's lost when the file gets averaged)
	wqt.addsourcefield(avg_1m, "WQ_SOURCE", gain_file)

	# add gain setting information
	avg_1m['Gain'] = gain

	# add site information
	avg_1m['Site'] = site

	# if shapefile provided try joining using the site field
	if sample_sites_shp is not None:
		if isinstance(sample_sites_shp, list):
			sites_shp_df = wqt.gps_append_fromlist(sample_sites_shp)
		else:
			# convert shapefile into pandas dataframe using function from wqt_timestamp_match
			sites_shp_df = wqt.wqtshp2pd(sample_sites_shp)

		# join using the site names from an attribute field
		gain_w_xy = gain_join_gps_by_site(avg_1m, sites_shp_df)

		# check that there is data in the join
		if gain_w_xy.size == 0:
			logging.warning("Unable to add XY coords. Make sure GPS file has {} as an attribute in Site field".format(site))
		else:
			avg_1m = gain_w_xy

	# add row to database table vertical_profiles
	gain_wq_df2database(avg_1m)

	return

