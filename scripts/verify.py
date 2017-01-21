from datetime import datetime

import arcpy
import pandas as pd

import geodatabase_tempfile

import waterquality
from waterquality import classes, funcs as wq_funcs
from waterquality import api
import scripts
from scripts import mapping

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


def verify_summary_file(month, year, summary_file,max_point_distance="5 Meters", max_missing_points=25):
	"""
		Given a path to a file and a list of datetime objects, loads the summary file data and verifies the data for each date has been entered into the DB
	:param summary_file_path:
	:param dates:
	:param date_field:
	:param time_format_string:
	:return:
	"""

	temp_points = geodatabase_tempfile.create_gdb_name("arcroject", scratch=True)
	try:
		mapping.generate_layer_for_month(month, year_to_use=year, output_location=temp_points)
	except scripts.NoRecordsError:
		print("DATE FAILED: {} {} - no records found for that date\n".format(month, year))
		raise

	# copy it out so we can add the Near fields
	temp_summary_file_location = geodatabase_tempfile.create_gdb_name("arcrproject_summary_file", scratch=True)
	print("Verification feature class at {}".format(temp_summary_file_location))
	arcpy.CopyFeatures_management(summary_file, temp_summary_file_location)
	print('Running Near to Find Missing Locations')
	arcpy.Near_analysis(temp_summary_file_location, temp_points, max_point_distance)

	print("Reading Results for Missing Locations")
	print("")
	missing_locations = arcpy.da.SearchCursor(
		in_table=temp_summary_file_location,
		field_names=["GPS_Date", "NEAR_FID"],
		where_clause="NEAR_FID IS NULL OR NEAR_FID = -1",
	)

	num_missing = 0
	missing_dates = {}

	for point in missing_locations:
		num_missing += 1
		missing_dates[datetime.strftime(point[0], "%x")] = 1  # use the locale-appropriate date as the key in the dictionary

	status = None

	if num_missing > max_missing_points:  # if we cross the threshold for notification
		print("CROSSED THRESHOLD: {} Missing Points. Possibly missing transects".format(num_missing))
		for key in missing_dates.keys():
			print("Unmatched point(s) on {}".format(key))
			status = False
	else:
		status = True
		print("ALL ClEAR for {} {}".format(month, year))

	print("\n")

	return status
