import os
import unittest

import scripts
from scripts import mapping
from waterquality import classes
import datetime

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

	def test_mapping_by_date(self):
		date_with_records = datetime.datetime.strptime("04/04/2013", "%m/%d/%Y")
		date_without_records = datetime.datetime.strptime("01/01/2012", "%m/%d/%Y")

		mapping.layer_from_date(date_with_records, os.path.join("test_export_folder", "test_export_for_date.shp"))

		self.assertRaises(scripts.NoRecordsError, mapping.layer_from_date, date_without_records, os.path.join("test_export_folder", "test_export_for_date.shp"))