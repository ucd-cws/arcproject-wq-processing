import os
import unittest

from scripts import mapping
from waterquality import classes


class BaseMapTest(unittest.TestCase):
	def setUp(self):
		self.session = classes.get_new_session()
		self.query = self.session.query(classes.WaterQuality).filter(classes.WaterQuality.site_id == 1)

	def test_query_to_shp(self):
		mapping.query_to_features(self.query,
								  r"C:\Users\dsx.AD3\Code\arcproject-wq-processing\scripts\tests\test_export_folder\test_wq.shp")

