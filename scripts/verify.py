from datetime import datetime

import arcpy

from waterquality import classes
from scripts import wqt_timestamp_match

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


def verify_date(verification_date, summary_file, date_field="Date_Time", time_format_string="%m/%d/%Y_%H:%M:%S%p"):
	v = SummaryFile(summary_file, date_field, time_format_string)


	return v

def get_wq_for_date

def read_summary_file_points(summary_file):
	pass