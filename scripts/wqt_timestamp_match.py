# -*- coding: utf-8 -*-
from __future__ import print_function

# match shp and water quality data by timestamp

# import standard library items
import os
from datetime import datetime, timedelta
import logging
import tempfile
import traceback

# import major third party modules
import six
import pandas as pd
import numpy as np
import arcpy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import exc

# import CWS modules
import geodatabase_tempfile

# import project modules
from waterquality import classes

# define constants
source_field = "WQ_SOURCE"
projection_spatial_reference = 3310  # Teale Albers  # 26942  # CA State Plane II Meters

# the following dict of dicts is to convert units when they vary in the data frame - look up the field and if there's
# a dict there, then look up the unit provided. If there's a number there, it's a multiplier to convert units to the desired
# standard units for that field

unit_conversion = {
	u"DEP25": {
		u"meters": None,
		u"feet": 0.3048,
	},
	u"DEPX": {
		u"meters": None,
		u"feet": 0.3048,
	},
	u"DEP200": {
		u"meters": None,
		u"feet": 0.3048,
	},
	u"DepthX": {
		u"meters": None,
		u"feet": 0.3048,
		u"volts": 0,  # check if can just pass Null value
	},
	u"Temp": {
		u"°C": None,
	},
	u"SpCond": {
		u"µS/cm": None,
		u"mS/cm": 1000,
	},
	u"DO%": {
		u"Sat": None
	},
	u"DO_PCT": {
		u"Sat": None
	},
	u"DO": {
		u"mg/l": None
	},
	u"PAR": {
		u"µE/s/m²": None
	},
	u"RPAR": {
		u"µE/s/m²": None
	},
	u"TurbSC": {
		u"NTU": None,
		# u"Volts": 0,  # check if can just pass Null value
	},
	u"CHL": {
		u"µg/l": None
	},
	u"CHL_VOLTS": {
		u"Volts": None
	},
	u"Sal": None,
	u"pH": None,
	u"Date": None,
	u"Time": None,
	u"Date_Time": None,
	u"WQ_SOURCE": None,
	u"GPS_SOURCE": None,
	u"GPS_Time": None,
	u"GPS_Date": None,
	u"POINT_Y": None,
	u"POINT_X": None,
	u"IBatt": None,
	u"EBatt": None,
	u"TurbSCV": None,
	u"pHVolts": None,
	u"Circ": None,
	u"Wiper": None,
	u"SpCond1": None,

}


def get_unit_conversion_scale(field, current_units):
	"""
		Looks up the scaling factors in unit_conversion and returns the appropriate value or None. When it returns None
		no scaling should be applied.
	:param field: the name of the field in the data frame we're looking up for scaling
	:param current_units: the units as described in the sonde data file
	:return: scaling value to be multiplied against entire field or None
	"""
	if field in unit_conversion:
		if unit_conversion[field] is None:
			return None

		if current_units in unit_conversion[field]:
			return unit_conversion[field][current_units]

	# serves as an automatic else to the above - if we didn't return, then this gets raised
	raise KeyError("Units on field {} not known. Can't continue loading without being sure that units are the same."
				   " The software will need to be updated with any scaling factors necessary to convert the units".format(field))


def check_and_convert_units(data_frame, units):
	"""
		Confirms that units are correct on each field we import and if they aren't converts them
	:param data_frame: a pandas data frame of water quality measurements
	:return: the same data frame with converted units
	"""

	fields = data_frame.columns.values.tolist()  # why this is the best way to get the fields is beyond me... http://stackoverflow.com/questions/19482970/get-list-from-pandas-dataframe-column-headers

	for field in fields:
		scaling_value = get_unit_conversion_scale(field, units[field])
		if scaling_value:
			if pd.__version__ >= "0.17.0":
				data_frame[field] = pd.to_numeric(data_frame[field])  # before multiplying, we have to cast the data to numeric
			else:
				data_frame[field] = data_frame[field].convert_objects(convert_numeric=True)

			data_frame[field] = data_frame[field].multiply(scaling_value)

	return data_frame


def make_units_index(row):
	"""
		Given the row of the data frame that has the units listed, makes a dictionary index of those values that can
		be looked up by field
	:param row: First row of the data frame that contains the units - created using data_frame.head(1)
	:return: dict index of units - keyed by field name
	"""

	units = {}
	for field in row:
		units[field] = row[field][0]

	return units


def convert_file_encoding(in_file, target_encoding="utf-8"):
	"""
		pandas chokes loading the documents if they aren't encoded as UTF-8 on Python 3.
		This creates a copy of the file that's converted to UTF-8 and is called before reading the CSV when running Python 3.

		Adapted from http://stackoverflow.com/a/191455/587938
	:param in_file:
	:param target_encoding:
	:return: path to converted file
	"""

	source = open(in_file)
	original_name = os.path.splitext(os.path.split(in_file)[1])[0]  # get the original filename by splitting off the extension and path

	new_file = tempfile.mktemp(prefix="{}__".format(original_name), suffix="converted_encoding")
	target = open(new_file, "wb")

	target.write(six.text_type(source.read()).encode(target_encoding))
	target.close()

	return new_file


def rename_depthfield(wq_df, depth_synonyms):
	"""
	Replaces depth field synonymes (DEPX, DEP200, etc) with DEP25
	:param wq_df: raw data frame of water quality values
	:param depth_synonyms: list of synonyms for the depth field (note must all be equivelent units)
	:return: wq_df with the depth field renamed to DEP25
	"""
	for syn in depth_synonyms:
		if syn in wq_df.columns:
			wq_df['DEP25'] = wq_df[syn]
	return wq_df


# load a water quality file
def wq_from_file(water_quality_raw_data):
	"""
	:param water_quality_raw_data: raw data file containing water quality data
	:return: water quality as pandas dataframe
	"""
	# load data from the csv starting at row 11, combine Date/Time columns using parse dates
	if six.PY3:  # pandas chokes loading the documents if they aren't encoded as UTF-8 on Python 3. This creates a copy of the file that's converted to UTF-8.
		water_quality_raw_data = convert_file_encoding(water_quality_raw_data)
		encoding = "utf-8"
	else:
		encoding = "latin_1" # absolutely necessary. Without this, Python 2 assumes it's in ASCII and then our units line (like the degree symbol) is gibberish and can't be compared

	wq = pd.read_csv(water_quality_raw_data, header=9, parse_dates=[[0, 1]], na_values=['#', '*'], encoding=encoding)  # TODO add other error values (2000000.00 might be error for CHL)

	# drop all columns that are blank since data in csv is separated by empty columns
	wq = wq.dropna(axis=1, how="all")

	# replace illegal fieldnames
	wq = replaceIllegalFieldnames(wq)

	units = make_units_index(wq.head(1))  # before we drop the units row, make a dictionary of the units for each field
	# drop first row which contains units with illegal characters
	wq = wq.drop(wq.index[[0]])

	# handles any unit scaling/converting we need to do for fields that aren't always in the same units
	wq = check_and_convert_units(wq, units)

	# rename depth field
	wq = rename_depthfield(wq, ["DEPX", "DEP200", "DepthX"])

	# add column with source filename
	addsourcefield(wq, source_field, water_quality_raw_data)

	# change Date_Time to be ISO8603 (ie no slashes in date)
	try:
		wq['Date_Time'] = pd.to_datetime(wq['Date_Time']) #, format='%m/%d/%Y %H:%M:%S')

	except ValueError:
		# still having it raise a new ValueError since that will stop execution, but provide this simpler message
		raise ValueError("Time is in a format that is not supported. Try using '%m/%d/%Y %H:%M:%S' .")

	return wq


def feature_class_to_pandas_data_frame(feature_class, field_list):
	"""
	Adapted from http://joelmccune.com/arcgis-to-pandas-data-frame/
	Load data into a Pandas Data Frame for subsequent analysis.

	Our use of this code requires ArcGIS 10.4 or Pro 1.3 or above because we need datetimes in numpy arrays.
	The function exists from 10.1 through 10.3 as well, but datetimes aren't allowed and an error is thrown.

	:param feature_class: Input ArcGIS Feature Class.
	:param field_list: Fields for input.
	:return: Pandas DataFrame object.
	"""
	return pd.DataFrame(
		arcpy.da.FeatureClassToNumPyArray(
			in_table=feature_class,
			field_names=field_list,
			skip_nulls=False,
			null_value=-99999
		)
	)


def TimestampFromDateTime(date, time):
	"""
	Returns python datetime object
	:param date: a date in format of %Y-%m-%d
	:param time: a time in format of %I:%M:%S%p
	:return: datetime object
	"""
	dt = date + 't' + time
	date_object = datetime.strptime(dt, '%Y-%m-%dt%I:%M:%S%p')
	return date_object


def reproject_features(feature_class):
	"""
	Given a feature class, it make a temporary file for it and reprojects the data to that location

	:param feature_class: the path to a feature class to be reprojected
	:return: reprojected feature class
	"""

	projected = geodatabase_tempfile.create_gdb_name()
	spatial_reference = arcpy.SpatialReference(projection_spatial_reference)

	arcpy.Project_management(feature_class, projected, spatial_reference)

	return projected


def check_projection(feature_class):
	"""
		Does two things. First, it confirms that the input data has a defined projection. This is something that was done
		manually in the SOP, so this will handle that. If it's not defined, it defines it as GCS WGS 1984.

		Second, it reprojects the data to the coordinate system of interest, as defined in projection_spatial_reference
	:param feature_class: The input feature class to check the projection of
	:return: feature class with corrected projection
	"""
	desc = arcpy.Describe(feature_class)
	try:
		if desc.spatialReference.factoryCode == 0:
			# spatial reference code 4326 is GCS WGS 1984. It's the default for the GPS
			arcpy.DefineProjection_management(feature_class, arcpy.SpatialReference(4326))
			desc = arcpy.Describe(feature_class)  # we need to refresh this afterward because it won't autoupdate and we need it for the next check

		if desc.spatialReference.factoryCode != projection_spatial_reference:
			feature_class = reproject_features(feature_class)
	finally:
		del desc

	return feature_class


def wqtshp2pd(feature_class):
	"""
	Add XY coords, converts wq transect shp into a pandas dataframe, adds source field, merges GPS_Data and GPS_Time into date_object
	:param feature_class: input shapefile
	:return: geopandas data frame
	"""

	# make a temporary copy of the shapefile to add xy data without altering original file

	feature_class = check_projection(feature_class)

	arcpy.MakeFeatureLayer_management(feature_class, "wqt_xy")
	try:
		# check if XY coords exist
		fields = arcpy.ListFields("wqt_xy", 'POINT_')

		if len(fields) != 2:
			# add XY points (POINT_X and POINT_Y to shapefile attribute table
			arcpy.AddXY_management("wqt_xy")  # CHECK - does this add xy to the original file everytime?

		# list of field names that can be converted to pandas df
		# http://gis.stackexchange.com/questions/151357/ignoring-field-types-in-python-list-returned-by-arcpy-listfields
		# Data must be 1-dimensional
		f_list = [f.name for f in arcpy.ListFields("wqt_xy") if
				  f.type not in ["Geometry", "OID", "GUID", "GlobalID"]]  # ignores geo, ID fields

		# convert attribute table to pandas dataframe
		df = feature_class_to_pandas_data_frame("wqt_xy", f_list)

		addsourcefield(df, "GPS_SOURCE", feature_class)

		# cast Date field to str instead of timestamp
		df["GPS_Date"] = df["GPS_Date"].dt.date.astype(str)  # ArcGis adds some artificial times

		# combine GPS date and GPS time fields into a single column
		df['Date_Time'] = df.apply(lambda row: TimestampFromDateTime(row["GPS_Date"], row["GPS_Time"]), axis=1)

		# drop duplicated rows in the data frame
		#df = df.drop_duplicates(["Date_Time"], 'first')

		# delete temporary feature layer
	finally:  # regardless, if there's an exception, delete the feature layer so other tests can complete
		arcpy.Delete_management("wqt_xy")

	return df


def replaceIllegalFieldnames(df):
	"""
	Renames fieldnames
	:param df: dataframe with bad fieldnames
	:return: dataframe with replaced fieldnames
	"""
	df = df.rename(columns={'CHL.1': 'CHL_VOLTS', 'DO%': 'DO_PCT', 'DEPX': 'DEP25'})  # TODO make this catch other potential errors
	return df


def dstadjustment(df, offset_hours):
	df2 = df.copy()  # make a copy of data so original is not overwritten
	dstshift = lambda x: x + timedelta(hours=offset_hours)
	df2['Date_Time'] = df2['Date_Time'].map(dstshift)
	return df2


def addsourcefield(dataframe, fieldName, source):
	"""
	Adds a new column to a dataframe and fills in the values from the basename of the source path
	:param dataframe: destination dataframe to modify
	:param fieldName: name of the new field that is to be added
	:param source: the full path of the data source
	:return: dataframe with a new column filled in with the source info
	"""
	base = os.path.basename(source)
	dataframe[fieldName] = base
	return


def JoinByTimeStamp(wq_df, shp_df):
	"""
	Joins geopandas dataframe with the water quality attributes using common Date Time fields
	:param wq_df: water quality data frame
	:param shp_df: geo dataframe from the shapefile
	:return: geopandas dataframe with water quality data and gps coordinates
	"""
	joined = pd.merge(shp_df, wq_df, how="outer", on="Date_Time")
	return joined


def splitunmatched(joined_data):
	"""
	Takes the joined dataframe amd splits into 3 dataframes with no NAs, no geo match, no wq match
	:param joined_data: result from JoinByTimeStamp()
	:return: 3 dataframes - all matches, wq rows with no gps data, and gps rows with no wq data
	"""
	# returns all joined data that has a match (ie inner join),
	# the unmatched transect points (outer left) and unmatched water quality (outer right) points as separate dataframes

	match = joined_data.dropna(subset=["GPS_SOURCE", source_field], how='any')
	no_geo = joined_data[joined_data["GPS_SOURCE"].isnull()]
	no_wq = joined_data[joined_data[source_field].isnull()]

	return match, no_geo, no_wq


def JoinMatchPercent(original, joined):
	"""
	Calculates how well the joined data matches the original
	:param original: water quality dataframe
	:param joined: water quality + GPS matches as dataframe
	:return: percentage of number of rows in match divided by number of rows in original
	"""
	percent_match = float(joined.shape[0]) / float(original.shape[0]) * 100
	return percent_match


def wq_append_fromlist(list_of_wq_files):
	"""
	Takes a list of water quality files and appends them to a single dataframe
	:param list_of_wq_files: list of raw water quality files paths
	:return: single dataframe with all the inputs
	"""
	master_wq_df = pd.DataFrame()
	for wq in list_of_wq_files:
		try:
			pwq = wq_from_file(wq)
			# append to master wq
			master_wq_df = master_wq_df.append(pwq)

		except:
			print("Unable to process: {}".format(wq))

	return master_wq_df


def gps_append_fromlist(list_gps_files):
	"""
	Merges multiple gps files into single geopandas dataframe
	:param list_gps_files: list of paths for gps files
	:return: single geopandas dataframe for all the input files
	"""
	master_pts = pd.DataFrame()
	for gps in list_gps_files:
		try:
			# shapefile for transect
			pts = wqtshp2pd(gps)

			# append to master wq
			master_pts = master_pts.append(pts)

		except:
			print("Unable to process: {}".format(gps))

	return master_pts

# set the default settings for parsing the site codes (and gain settings) from the filename spliting on underscores
site_function_params = {"site_part": 2,
                        "gain_part": 4}


def site_function_historic(*args, **kwargs):
	"""
	Site functions are passed to wq_df2database so that it can determine which site a record is from. Historic data
	will use this function since it will parse if off the data frame as constructed in this code (which includes
	a field for the filename, which has the site code). Future data will have another method and use a different site
	function that will be passed to wq_df2database

	:param args:
	:param kwargs:
	:return: site object
	"""

	record = kwargs["record"]  # unpacking this way because I want it to be able to accept the kinds of args another function might receive too, since the caller will pass a bunch
	session = kwargs["session"]  # database session from caller
	site_part = kwargs["site_part"]
	filename = record.get(source_field)  # get the value of the data source field (source_field defined globally)
	try:
		filename = os.path.splitext(filename)[0]
		site_code = filename.split("_")[int(site_part)].upper()  # the third item in the underscored part of the name has the site code
	except IndexError:
		raise IndexError("Filename was unable to be split based on underscore in order to parse site name - be sure your filename format matches the site function used, or that you're using the correct site retrieval function")

	try:
		q = session.query(classes.Site).filter(classes.Site.code == site_code).one()
	except NoResultFound:
		raise ValueError("Skipping record with index {}. Site code [{}] not found.".format(record.get("Index"), site_code))

	return q  # return the session object


def wq_df2database(data, field_map=classes.water_quality_header_map, site_function=site_function_historic,
                   site_func_params=site_function_params, session=None):
	"""
	Given a pandas data frame of water quality records, translates those records to ORM-mapped objects in the database.

	:param data: a pandas data frame of water quality records
	:param field_map: a field map (dictionary) that translates keys in the data frame (as the dict keys) to the keys used
		in the ORM - uses a default, but when the schema of the data files is different, a new field map will be necessary
	:param site_function: the object of a function that, given a record from the data frame and a session, returns the
		site object from the database that should be associated with the record
	:param site_func_params: parameters to pass to the site function
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
			make_record(field_map, row[1], session, site_function, site_func_params)  # row[1] is the actual data included in the row

		# session.add_all(records)
		if session_created:  # only commit if this function created the session - otherwise leave it to caller
			try:
				session.commit()  # saves all new objects
			except exc.IntegrityError as e:
				print(e)
				print("The water quality data you are adding to the database already exists in the database. If only some of your data is in the database, you may need to remove the overlapping data and only add the unique data.")
	finally:
		if session_created:
			session.close()


def site_from_text(site_code, session):
	"""
		Given a site code and an open database session, returns the site object
	:param site_code: a text string that matches a site code in the database
	:param session: An open database session
	:return: Site object
	"""
	return session.query(classes.Site).filter(classes.Site.code == site_code).one()


def make_record(field_map, row, session, site_function, site_func_params):
	"""
	 	Called for each record in the loaded and joined Pandas data frame. Given a named tuple of a row in the data frame, translates it into a waterquality object
	:param field_map: A field map dictionary with keys based on the data frame fields and values of the corresponding database field
	:param row: a named tuple of the row in the data frame to translate into the WaterQuality object
	:param session: an open SQLAlchemy database session
	:param site_function: A site code or function that identifies the site and returns the site object for the record.
	:param site_func_params: parameters to pass to the site function
	:return:
	"""
	wq = classes.WaterQuality()  # instantiates a new object

	try:  # figure out whether we have a function or a text code to determine the site. If it's a text code, call site_from_text, otherwise call the function
		if isinstance(site_function, six.string_types):
			wq.site = site_from_text(site_code=site_function, session=session)
		else:
			wq.site = site_function(record=row, session=session, **site_func_params)  # run the function to determine the record's site code
	except ValueError:
		traceback.print_exc()
		return  # breaks out of this loop, which forces a skip of adding this object

	wq.spatial_reference_code = projection_spatial_reference  # set the record's spatial reference to what was used to reproject it.

	for key in row.index:  # converts named_tuple to a Dict-like and gets the keys
		# look up the field that is used in the ORM/database using the key from the namedtuple. If it doesn't exist, throw a warning and move on to next field
		try:
			class_field = field_map[key]
		except KeyError:
			#logging.warning("Skipping field {} with value {} for record {}. Field not found in field map.".format(key, row.get(key), row))
			continue

		if class_field is None:  # if it's an explicitly defined None and not nonexistent (handled in above exception), then skip it silently
			continue

		try:
			setattr(wq, class_field, row.get(key))  # for each value, it sets the object's value to match
		except AttributeError:
			print("Incorrect field map - original message was {}".format(traceback.format_exc()))

	else:  # if we don't break for a bad site code or something else, then add the object
		session.add(wq)  # and adds the object for creation in the DB - will be committed later before the session is closed.


def dict_field_types(df):
	"""
	Creates a python dictonary with the field names and field types (converting the field types to feature class supported)
	:param df: pandas dataframe
	:return: data dict with field info : fieldname = dtype(field)
	"""
	# create dict using the current data types
	d = df.dtypes.to_dict()

	# iterate through the items in the dict changing the field types
	for item in d:
		# converts timestamps with nanoseconds to microseconds
		if d[item] == np.dtype('<M8[ns]'):
			d[item] = np.dtype('<M8[us]')
		# convert objects into strings
		elif d[item] == np.dtype('O'):
			d[item] = np.dtype('S32')  # converts object to strings (string length must be set)
		elif d[item] == np.dtype('<i8'):  # int64 not supported - needs to be made a float64 (double) - see http://pro.arcgis.com/en/pro-app/arcpy/get-started/working-with-numpy-in-arcgis.htm
			d[item] = np.dtype('<f8')
	return d


def pd2np(pandas_dataframe):
	"""
	Converts a pandas dataframe into a numpy structured array with field names and NumPy dtypes.
	:param pandas_dataframe:
	:return: numpy array to convert to feature class
	"""

	# replace NAs with -9999
	pandas_dataframe = pandas_dataframe.fillna(-9999)

	x = np.array(np.rec.fromrecords(pandas_dataframe.values))
	names = pandas_dataframe.dtypes.index.tolist()
	x.dtype.names = tuple(names)

	# change field types
	field_dtypes = dict_field_types(pandas_dataframe)

	if six.PY2:
		new_types = field_dtypes.items()
	elif six.PY3:
		new_types = list(field_dtypes.items())  # need to cast to a list on Python 3

	# casts fields to new dtype (wq variables to float, date_time field to esri supported format
	x = x.astype(new_types)  # arcpy np to fc only supports specific datatypes (date '<M8[us]'

	return x


def np2feature(np_array, output_feature, spatial_ref):
	"""
	uses arcpy to convert numpy structured array into a feature class
	:param np_array: structured numpy array with XY fields to convert
	:param output_feature: location to save the output feature
	:param spatial_ref: defined spatial reference for the output feature class
	:return:
	"""
	# set projection info using spatial_ref = arcpy.Describe(input).spatialReference
	arcpy.da.NumPyArrayToFeatureClass(np_array, output_feature, ("POINT_X", "POINT_Y"), spatial_ref)
	return


def dst_closest_match(wq, pts):
	"""
	Test shifting timestamp by +1, 0, -1 hour to account for daylight saving time errors
	:param wq: data frame with water quality data
	:param pts: dataframe from the shapefile
	:return: water quality data frame with the highest percentage match to the timestamps in the shapefile
	"""
	offsets = {}
	# determine if file neesd to be adjusted for DST in either direction by testing variants and selecting the one
	# that matches the most records
	for i in [-1, 0, 1]:
		# offset water quality
		off = dstadjustment(wq, i)

		# try joining by timestamp
		off_joined_data = JoinByTimeStamp(off, pts)
		off_matches = splitunmatched(off_joined_data)[0]

		# report the percentage matched
		percent_match = JoinMatchPercent(wq, off_matches)

		# add to dict
		offsets[i] = percent_match

	# best match for the offsets
	highest_percent_offset = max(offsets, key=offsets.get)

	# apply offset to the original data
	offset_df = dstadjustment(wq, highest_percent_offset)
	return offset_df


def main(water_quality_files, transect_gps, output_feature=None, site_function=site_function_historic,
         site_func_params=site_function_params, dst_adjustment=False):
	"""
	:param water_quality_files: list of water quality files collected during the transects
	:param transect_gps: gps shapefile of transect tract
	:param output_feature: OPTIONAL location to save the water quality  shapefile with data matched by timestamps
	:param site_function: A site code or function that identifies the site and returns the site object for the record.
	:param site_func_params: parameters to pass to the site function
	:param dst_adjustment: boolean to control if to adjust for daylight saving time
	:return:
	"""

	# water quality
	wq = wq_append_fromlist(water_quality_files)

	# shapefile for transect
	if isinstance(transect_gps, list):  # checks if a list was passed to the parameter
		pts = gps_append_fromlist(transect_gps)  # append all the individual gps files to singe dataframe
	else:
		pts = wqtshp2pd(transect_gps)

	# DST adjustment
	if dst_adjustment:
		wq = dst_closest_match(wq, pts)

	# join using time stamps with exact match
	joined_data = JoinByTimeStamp(wq, pts)
	matches = splitunmatched(joined_data)[0]

	print("Percent Matched: {}".format(JoinMatchPercent(wq, matches)))

	wq_df2database(matches, site_function=site_function, site_func_params=site_func_params)

	if output_feature:
		# Define a spatial reference for the output feature class by copying the input
		spatial_ref = arcpy.Describe(transect_gps).spatialReference

		# convert pandas dataframe to structured numpy array
		match_np = pd2np(matches)

		# convert structured array to output feature class
		np2feature(match_np, output_feature, spatial_ref)
	return
