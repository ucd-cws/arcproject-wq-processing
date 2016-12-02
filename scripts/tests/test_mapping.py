import os
import unittest

from scripts import mapping
from waterquality import classes

import arcpy

class BaseMapTest(unittest.TestCase):
	def setUp(self):
		self.session = classes.get_new_session()
		self.query = self.session.query(classes.WaterQuality).filter(classes.WaterQuality.site_id == 1)
		self.output = os.path.join("test_export_folder", "test_wq.shp")

	def test_query_to_shp(self):

		# clean up before test
		if arcpy.Exists(self.output):
			arcpy.Delete_management(self.output)

		mapping.query_to_features(self.query, self.output)