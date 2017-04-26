import os
import sys
import shutil
import unittest
import datetime

import arcpy

import amaptor
import geodatabase_tempfile

import scripts.exceptions
from arcproject import scripts
from arcproject.scripts import mapping
from arcproject.waterquality import classes
from arcproject.scripts import config

folder_path = os.path.dirname(os.path.abspath(__file__))

class BaseMapTest(unittest.TestCase):
	def setUp(self):
		self.session = classes.get_new_session()
		self.query = self.session.query(classes.WaterQuality).filter(classes.WaterQuality.site_id == 1)
		self.output = os.path.join(folder_path, "test_export_folder", "test_wq.shp")

	def test_query_to_shp(self):

		# clean up before test
		if arcpy.Exists(self.output):
			arcpy.Delete_management(self.output)

		mapping.query_to_features(self.query, self.output)

	def test_mapping_by_date(self):
		date_with_records = datetime.datetime.strptime("04/04/2013", "%m/%d/%Y")
		date_without_records = datetime.datetime.strptime("01/01/2012", "%m/%d/%Y")

		mapping.layer_from_date(date_with_records, os.path.join(folder_path, "test_export_folder", "test_export_for_date.shp"))

		self.assertRaises(scripts.exceptions.NoRecordsError, mapping.layer_from_date, date_without_records, os.path.join("test_export_folder", "test_export_for_date.shp"))


class TestMakeNewMap(unittest.TestCase):
	def test_pro_new_map(self):

		if amaptor.ARCMAP:  # this test is ArcGIS Pro specific
			return

		toolbox_path = os.path.join(folder_path, "arcproject_toolbox.py")
		shutil.copyfile(os.path.join(config.arcwqpro, "wq-processing-toolbox.pyt"), toolbox_path)
		sys.path.append(folder_path)

		import arcproject_toolbox
		arcproject_toolbox.testing_project = os.path.join(folder_path, "testfiles", "blank_pro_project_working.aprx")
		try:
			shutil.copyfile(os.path.join(folder_path, "testfiles", "blank_pro_project.aprx"), arcproject_toolbox.testing_project)

			class param(object):
				def __init__(self, value=None):
					self.valueAsText = str(value)
					self.value = value

			tool = arcproject_toolbox.GenerateMap()

			params = [param(2016), param("May"), param("CHL"), param("testing_map"), param(), param()]
			tool.execute(parameters=params, messages=None)
		finally:
			os.remove(toolbox_path)
			os.remove(arcproject_toolbox.testing_project)


if __name__ == '__main__':
	unittest.main()
