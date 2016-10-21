# match shp and water quality data by timestamp
import pandas as pd
import arcpy
import os
from datetime import datetime, timedelta

from waterquality import classes
import numpy as np


# load a water quality file
def wq_from_file(water_quality_raw_data):
	"""
	:param water_quality_raw_data: raw data file containing water quality data
	:return: water quality as pandas dataframe
	"""
	# load data from the csv starting at row 11, combine Date/Time columns using parse dates
	wq = pd.read_csv(water_quality_raw_data, header=9, parse_dates=[[0, 1]], na_values='#') # TODO add other error values (2000000.00 might be error for CHL)

	# drop first row which contains units with illegal characters
	wq = wq.drop(wq.index[[0]])

	# drop all columns that are blank since data in csv is separated by empty columns
	wq = wq.dropna(axis=1, how="all")

	# replace illegal fieldnames
	wq = replaceIllegalFieldnames(wq)

	# add column with source
	addsourcefield(wq, "WQ_SOURCE", water_quality_raw_data)

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


def wqtshp2pd(shapefile):
	"""
	Add XY coords, converts wq transect shp into a pandas dataframe, adds source field, merges GPS_Data and GPS_Time into date_object
	:param shapefile: input shapefile
	:return: geopandas data frame
	"""

	# make a temporary copy of the shapefile to add xy data without altering original file
	arcpy.MakeFeatureLayer_management(shapefile, "wqt_xy")

	# check if XY coords exist
	fields = arcpy.ListFields("wqt_xy", 'POINT_')

	if len(fields) != 2:
		# add XY points (POINT_X and POINT_Y to shapefile attribute table
		arcpy.AddXY_management("wqt_xy")  # CHECK - does this add xy to the original file everytime?

	# convert attribute table to pandas dataframe
	df = feature_class_to_pandas_data_frame("wqt_xy", ["GPS_Date", "GPS_Time", "POINT_X", "POINT_Y"]) # TODO "*" returns all fields


	addsourcefield(df, "GPS_SOURCE", shapefile)

	# cast Date field to str instead of timestamp
	df["GPS_Date"] = df["GPS_Date"].dt.date.astype(str)  # ArcGis adds some artificial times

	# combine GPS date and GPS time fields into a single column
	df['Date_Time'] = df.apply(lambda row: TimestampFromDateTime(row["GPS_Date"], row["GPS_Time"]), axis=1)

	# drop duplicated rows in the data frame
	#df = df.drop_duplicates(["Date_Time"], 'first')

	# delete temporary feature layer
	arcpy.Delete_management("wqt_xy")

	return df


def replaceIllegalFieldnames(df):
	"""
	Renames fieldnames
	:param df: dataframe with bad fieldnames
	:return: dataframe with replaced fieldnames
	"""
	df = df.rename(columns={'CHL.1': 'CHL_VOLTS', 'DO%': 'DO_PCT'}) # TODO make this catch other potential errors
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

	match = joined_data.dropna(subset=["GPS_SOURCE", "WQ_SOURCE"], how='any')
	no_geo = joined_data[joined_data["GPS_SOURCE"].isnull()]
	no_wq = joined_data[joined_data["WQ_SOURCE"].isnull()]

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


def wq_df2database(data, field_map):

	# TODO: Need to pass in a field map and make a default - allows variations on the data table to be handled
	# TODO: Handle case of attribute that trying to set not existing on the object
	# TODO: needs to retrieve the site object from the database, or get one passed in.

	session = classes.get_new_session()

	for row in data.itertuples():  # iterates over all of the rows in the data frames the fast way
		wq = classes.WaterQuality()  # instantiates a new object
		for key in vars(row).keys():  # converts named_tuple to a Dict-like and gets the keys
			if key == "Index":  # skips the Index key
				continue
			setattr(wq, key, getattr(row, key))  # for each value, it sets the object's value to match
		session.add(wq)  # and adds the object for creation in the DB

	session.commit()  # saves all new objects
	return


# TODO: account for different fields (ie create this automatically)
field_type_dict = {'GPS_Time': 'S10', 'Date_Time': '<M8[us]', 'PAR': '<f', 'Temp': '<f', 'Sal': '<f', 'DEP25': '<f', 'CHL': '<f', 'TurbSC': '<f', 'RPAR': '<f', 'SpCond': '<f', 'POINT_X': '<f8', 'POINT_Y': '<f8', 'GPS_Date': 'S10', 'pH': '<f', 'WQ_SOURCE': 'S21', 'GPS_SOURCE': 'S18', 'CHL_VOLTS': '<f'}


def pd2np(pandas_dataframe, field_dtypes):
	"""
	Converts a pandas dataframe into a numpy structured array with field names and NumPy dtypes.
	:param pandas_dataframe:
	:param field_dtypes: python dictoniary with field name and desired numpy data type to cast
	:return: numpy array to convet to feature class
	"""
	x = np.array(np.rec.fromrecords(pandas_dataframe.values))
	names = pandas_dataframe.dtypes.index.tolist()
	x.dtype.names = tuple(names)

	# casts fields to new dtype (wq variables to float, date_time field to esri supported format
	x = x.astype(field_dtypes.items()) # arcpy np to fc only supports specific datatypes (date '<M8[us]'

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


def main(water_quality_files, transect_gps, output_feature):
	"""
	:param water_quality_files: list of water quality files collected during the transects
	:param transect_gps: gps shapefile of transect tract
	:param output_feature: location to save the water quality shapefile
	:return: shapefile with water quality data matched by time stamps
	"""

	# water quality
	wq = wq_append_fromlist(water_quality_files)

	# shapefile for transect
	pts = wqtshp2pd(transect_gps)

	# join using time stamps with exact match
	joined_data = JoinByTimeStamp(wq, pts)
	matches = splitunmatched(joined_data)[0]

	print("Percent Matched: {}".format(JoinMatchPercent(wq, matches)))

	# Define a spatial reference for the output feature class by copying the input
	spatial_ref = arcpy.Describe(transect_gps).spatialReference

	# convert pandas dataframe to structured numpy array
	match_np = pd2np(matches, field_dtypes=field_type_dict)

	# convert structured array to output feature class
	np2feature(match_np, output_feature, spatial_ref)

	return

