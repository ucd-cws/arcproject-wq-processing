import arcpy
import geodatabase_tempfile

class NoRecordsError(ValueError):
	pass


class SpatialReferenceError(ValueError):
	pass


def reproject_features(feature_class, sr_code):
	"""
	Given a feature class, it make a temporary file for it and reprojects the data to that location

	:param feature_class: the path to a feature class to be reprojected
	:return: reprojected feature class
	"""

	projected = geodatabase_tempfile.create_gdb_name()
	spatial_reference = arcpy.SpatialReference(sr_code)

	arcpy.Project_management(feature_class, projected, spatial_reference)

	return projected