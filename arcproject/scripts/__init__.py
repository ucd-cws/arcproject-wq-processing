import arcpy
import geodatabase_tempfile

from arcproject.scripts import chl_decision_tree
from arcproject.scripts import chl_heatmap
from arcproject.scripts import chl_reg
from arcproject.scripts import config
from arcproject.scripts import linear_ref
from arcproject.scripts import mapping
from arcproject.scripts import slurp
from arcproject.scripts import sub_gen_heat
from arcproject.scripts import swap_site_recs
from arcproject.scripts import verification_tests
from arcproject.scripts import verify
from arcproject.scripts import wq_gain
from arcproject.scripts import wqt_timestamp_match

__all__ = ["chl_decision_tree", "chl_heatmap", "chl_reg", "config", "linear_ref", "mapping", "slurp",
		   "sub_gen_heat", "swap_site_recs", "verification_tests", "verify", "wq_gain", "wqt_timestamp_match"]

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