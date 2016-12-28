import os

import arcpy
import pandas as pd

from scripts.wqt_timestamp_match import pd2np

arcgis_pro_layer_symbology = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wq_points.lyrx")
arcgis_10_layer_symbology = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wq_points.lyr")


def set_output_symbology(parameter):
	## Output symbology
	if arcpy.GetInstallInfo()["ProductName"] == "ArcGISPro":
		parameter.symbology = arcgis_pro_layer_symbology
	else:
		parameter.symbology = arcgis_10_layer_symbology

	return parameter


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
		raise ValueError("Records have non-matching spatial reference - can't map.")
	else:
		sr_code = sr_codes[0]  # get what should be the only item in the sr_codes array

	sr = arcpy.SpatialReference(sr_code)  # make a spatial reference object

	arcpy.da.NumPyArrayToFeatureClass(
		in_array=pd2np(df),
		out_table=export_path,
		shape_fields=["x_coord", "y_coord"],
		spatial_reference=sr,
	)
