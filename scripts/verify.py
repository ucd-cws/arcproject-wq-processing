from datetime import datetime

import arcpy
import pandas as pd

import geodatabase_tempfile

import waterquality
from waterquality import classes, funcs as wq_funcs
from waterquality import api
from scripts import wqt_timestamp_match
import scripts
from scripts import mapping

try:
	from tqdm import tqdm
	has_tqdm = True
	print("Using progress bars")
except ImportError:
	has_tqdm = False

class Point(object):
	"""
		This could probably just be a three-tuple instead of a class, but this keeps things more consistent
	"""
	def __init__(self, x, y, date_time, format_string=None):
		self.x = x
		self.y = y
		self._date_time = date_time
		self.date_time = None  # will be set when extract_time is called

		if format_string:
			if format_string == "default":  # doing it this way so we don't have to hardcode the default in multiple places
				self.extract_time()
			else:
				self.extract_time(format_string)

	def extract_time(self, format_string="%m/%d/%Y_%H:%M:%S%p"):
		self.date_time = datetime.strptime(self._date_time, format_string)

	def __repr__(self):
		return "Point taken at {} at location {}, {}".format(self.date_time, self.x, self.y)


class SummaryFile(object):
	def __init__(self, path, date_field, time_format_string=None, setup_and_load=True):
		self.path = path
		self.points = []
		self.crs_code = None
		self.date_field = date_field
		self.time_format_string = time_format_string

		if setup_and_load:
			self.get_crs()
			self.load_points()

			if time_format_string:
				self.extract_time()

	def get_crs(self):
		desc = arcpy.Describe(self.path)
		self.crs_code = desc.spatialReference.factoryCode
		del desc

	def load_points(self):
		for row in arcpy.da.SearchCursor(self.path, ["SHAPE@XY", self.date_field]):
			self.points.append(Point(
								row[0][0],
								row[0][1],
								row[1]
								)
							)

	def extract_time(self):
		for point in self.points:
			point.extract_time(self.time_format_string)


def check_in_same_projection(summary_file, verification_date):
	"""
		Checks the summary file against the spatial reference of the records for a provided date - returns a reprojected version of it that matches the spatial reference of the stored features
	:param summary_file:
	:param verification_date:
	:return:
	"""

	# get some records
	wq = api.get_wq_for_date(verification_date)

	sr_code = wq_funcs.get_wq_df_spatial_reference(wq)
	return scripts.reproject_features(summary_file, sr_code)


def verify_summary_file(summary_file_path, dates=(), date_field="Date_Time", time_format_string="%m/%d/%Y_%H:%M:%S%p", max_point_distance="1.5 meters", max_missing_points=25):
	"""
		Given a path to a file and a list of datetime objects, loads the summary file data and verifies the data for each date has been entered into the DB
	:param summary_file_path:
	:param dates:
	:param date_field:
	:param time_format_string:
	:return:
	"""

	# reprojects the summary file to be in the same projection as the stored data
	summary_file_path = check_in_same_projection(summary_file_path, dates[0])

	# gets all the points loaded in with x/y values
	v = SummaryFile(summary_file_path, date_field, time_format_string)
	print("Summary file has {} points".format(len(v.points)))

	for day in dates:
		verify_date_v2(day, v, max_point_distance, max_missing_points)


def get_records_to_examine(wq, summary_file):
	s = wq.loc[wq["spatial_reference_code"] == summary_file.crs_code]
	return s.loc[s["Matched"] == 0]


def get_df_size(df):
	return int(df.size/df.shape[1])  # divide the size by the number of columns


def verify_date_v2(verification_date, summary_file, max_point_distance, max_missing_points):

	temp_points = geodatabase_tempfile.create_gdb_name("arcroject", scratch=True)
	mapping.layer_from_date(verification_date, temp_points)

	print('Running Near to Find Missing Locations')
	arcpy.Near_analysis(temp_points, summary_file, search_radius=max_point_distance)

	print("Reading Results for Missing Locations")
	missing_locations = arcpy.da.SearchCursor(
		in_table=temp_points,
		field_names=["id", "date_time", "y_coord", "x_coord", "NEAR_FID"],
		where_clause="NEAR_FID is NULL",
	)

	num_missing = 0
	missing_dates = {}
	for point in missing_locations:
		num_missing += 1
		missing_dates[datetime.strftime(point[1], "%x")] = 1  # use the locale-appropriate date as the key in the dictionary

	if num_missing > max_missing_points:  # if we cross the threshold for notification
		print("CROSSED THRESHOLD: Possibly missing transects")
		for key in missing_dates.keys():
			print("Unmatched point(s) on {}".format(key))



def verify_date(verification_date, summary_file):  # TODO: Possibly reproject summary file to match data

	# loads the water quality data from the database for that same day
	wq = api.get_wq_for_date(verification_date)
	print("{} records in database for date".format(get_df_size(wq)))
	df_len = get_df_size(wq)
	wq["Matched"] = pd.Series([0] * df_len, name="Matched")  # add a matched items flag with a default of 0 - [0] * df_len produces a list with df_len values.

	records_in_coordinate_system = get_records_to_examine(wq, summary_file)
	print("{} records in the same coordinate system as summary file".format(get_df_size(records_in_coordinate_system)))

	if has_tqdm:
		points = tqdm(summary_file.points)
	else:
		points = summary_file.points

	for point in points:
		short_x = waterquality.shorten_float(point.x, places=7)
		short_y = waterquality.shorten_float(point.y, places=7)

		records_at_x = records_in_coordinate_system.loc[records_in_coordinate_system["x_coord"] == short_x]
		matching_records = records_at_x.loc[records_at_x["y_coord"] == short_y]
		matching_records["Matched"] = 1
		records_in_coordinate_system = get_records_to_examine(wq, summary_file)

	matched = wq.loc[wq["Matched"] == 1]
	print("{} Matched locations".format(get_df_size(matched)))

	if len(summary_file.points) == 0:
		raise ValueError("No points found for date")
	else:
		return wq
