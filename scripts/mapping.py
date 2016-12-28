import os
import datetime

import arcpy
import pandas as pd

from waterquality import classes
from scripts.wqt_timestamp_match import pd2np

arcgis_pro_layer_symbology = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wq_points.lyrx")
arcgis_10_layer_symbology = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wq_points.lyr")


class NoRecordsError(ValueError):
	pass


class SpatialReferenceError(ValueError):
	pass


def set_output_symbology(parameter):
	## Output symbology
	if arcpy.GetInstallInfo()["ProductName"] == "ArcGISPro":
		parameter.symbology = arcgis_pro_layer_symbology
	else:
		parameter.symbology = arcgis_10_layer_symbology

	return parameter


def layer_from_date(date_to_use, output_location):
	"""
		Given a date and output location, exports records to a feature class
	:param date_to_use: date in MM/DD/YYYY format
	:param output_location: full path to output feature class
	:return: returns nothing
	"""

	wq = classes.WaterQuality
	session = classes.get_new_session()

	try:
		arcpy.AddMessage("Using Date {}".format(date_to_use))
		upper_bound = date_to_use.date() + datetime.timedelta(days=1)
		query = session.query(wq).filter(wq.date_time > date_to_use.date(), wq.date_time < upper_bound, wq.x_coord != None, wq.y_coord != None)  # add 1 day's worth of nanoseconds

		try:
			query_to_features(query, output_location)
		except NoRecordsError:
			arcpy.AddWarning("No records for date {}".format(date_to_use))
			raise
	finally:
		session.close()


def query_to_features(query, export_path):
	"""
	Given a SQLAlchemy query for water quality data, exports it to a feature class
	:param query: a SQLAlchemy query object
	:param export_path: the path to write out a feature class to
	:return:
	"""

	# read the SQLAlchemy query into a Pandas Data Frame since that can talk to ArcGIS
	df = pd.read_sql(query.statement, query.session.bind)

	# confirm that all of the items are in the same spatial reference - this should always be the case, but we should
	# make sure so nothing weird happens

	sr_codes = df.spatial_reference_code.unique()  # get all of the codes in use in this query
	if sr_codes.size > 1:  # if we have more than one code, sound the alarm
		raise SpatialReferenceError("Records have non-matching spatial reference - can't map.")
	elif sr_codes.size == 1:
		sr_code = sr_codes[0]  # get what should be the only item in the sr_codes array
	else:  # aka, if sr_codes.size == 0
		if df.size == 0:
			raise NoRecordsError("No records for query")
		else:
			raise SpatialReferenceError("No Spatial Reference attached to records in query - can't map!")

	sr = arcpy.SpatialReference(sr_code)  # make a spatial reference object

	arcpy.da.NumPyArrayToFeatureClass(
		in_array=pd2np(df),
		out_table=export_path,
		shape_fields=["x_coord", "y_coord"],
		spatial_reference=sr,
	)
