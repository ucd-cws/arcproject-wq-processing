import calendar
import datetime
import os

import arcpy
import pandas as pd

from scripts import NoRecordsError, SpatialReferenceError
from scripts.wqt_timestamp_match import pd2np
from waterquality import classes, funcs as wq_funcs

arcgis_pro_layer_symbology = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wq_points.lyrx")
arcgis_10_layer_symbology = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wq_points.lyr")


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
	:param date_to_use: date in MM/DD/YYYY format or a datetime object
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

	sr_code = wq_funcs.get_wq_df_spatial_reference(df)

	sr = arcpy.SpatialReference(sr_code)  # make a spatial reference object

	arcpy.da.NumPyArrayToFeatureClass(
		in_array=pd2np(df),
		out_table=export_path,
		shape_fields=["x_coord", "y_coord"],
		spatial_reference=sr,
	)


def generate_layer_for_month(month_to_use, output_location, year_to_use):
	wq = classes.WaterQuality
	session = classes.get_new_session()
	try:
		lower_bound = datetime.date(year_to_use, month_to_use, 1)
		upper_bound = datetime.date(year_to_use, month_to_use, int(calendar.monthrange(year_to_use, month_to_use)[1]))
		arcpy.AddMessage("Pulling data for {} through {}".format(lower_bound, upper_bound))
		query = session.query(wq).filter(wq.date_time > lower_bound, wq.date_time < upper_bound, wq.x_coord != None, wq.y_coord != None)  # add 1 day's worth of nanoseconds
		query_to_features(query, output_location)
	finally:
		session.close()