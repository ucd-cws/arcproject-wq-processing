import calendar
import datetime
import os

import arcpy
import pandas as pd

import amaptor

from . import NoRecordsError, SpatialReferenceError
from .wqt_timestamp_match import pd2np
from ..waterquality import classes, funcs as wq_funcs

_BASE_FOLDER = os.path.split(os.path.dirname(__file__))[0]
_TEMPLATES_FOLDER = os.path.join(_BASE_FOLDER, "templates", )
_LAYERS_FOLDER = os.path.join(_TEMPLATES_FOLDER, "layers")

arcgis_10_template = os.path.join(_TEMPLATES_FOLDER, "base_template.mxd")
arcgis_pro_template = os.path.join(_TEMPLATES_FOLDER, "arcproject_template_pro", "arcproject_template_pro.aprx")
arcgis_pro_layout_template = os.path.join(_TEMPLATES_FOLDER, "arcproject_template_pro", "main_layout.pagx")

arcgis_pro_layer_symbology = os.path.join(_LAYERS_FOLDER, "wq_points.lyrx")
arcgis_10_layer_symbology = os.path.join(_LAYERS_FOLDER, "wq_points.lyr")

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


def generate_layer_for_month(month_to_use, year_to_use, output_location):
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


def generate_layer_for_site(siteid, output_location):
	wq = classes.WaterQuality
	session = classes.get_new_session()
	try:
		query = session.query(wq).filter(wq.site_id == siteid, wq.x_coord != None, wq.y_coord != None)
		query_to_features(query, output_location)
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


def map_missing_segments(summary_file, loaded_data, output_location, template=os.path.join(_TEMPLATES_FOLDER, "base_template.mxd")):
	"""
		A mapping function used by data validation code to create maps when data is invalid
	:param summary_file:
	:param loaded_data:
	:param output_location:
	:param template:
	:return:
	"""

	transect_template = os.path.join(_LAYERS_FOLDER, "added_data.lyr")
	summary_file_template = os.path.join(_LAYERS_FOLDER, "summary_file_review.lyr")

	project = amaptor.Project(template)
	map = project.maps[0]
	map.insert_feature_class_with_symbology(summary_file, layer_file=summary_file_template, layer_name="Summary File",
											near_name="Arc_DeltaWaterways_0402", insert_position="BEFORE")
	map.insert_feature_class_with_symbology(loaded_data, layer_file=transect_template, layer_name="Loaded Transects",
											near_name="Arc_DeltaWaterways_0402", insert_position="BEFORE")

	project.save_a_copy(output_location)

	return project
