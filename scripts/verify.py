import arcpy

from waterquality import classes
from scripts import wqt_timestamp_match

class Point(object):
	"""
		This could probably just be a three-tuple instead of a class, but this keeps things more consistent
	"""
	def __init__(self, x, y, datetime):
		self.x = x
		self.y = y
		self.datetime = datetime

class SummaryFile(object):
	def __init__(self, path, date_field):
		self.path = path
		self.points = []
		self.crs_code = None
		self.date_field = date_field

	def get_crs(self):
		desc = arcpy.Describe(self.path)
		self.crs_code = desc.spatialReference.factoryCode
		del desc

	def load_points(self):
		for row in arcpy.da.SearchCursor(self.path, ["SHAPE@XY", self.date_field]):
			self.points.append(Point(
								row[0][0],
								row[0][1],
								row.getValue(self.date_field)
								)
							)

def verify_date(verification_date, summary_file):
	pass



def read_summary_file_points(summary_file):
	pass