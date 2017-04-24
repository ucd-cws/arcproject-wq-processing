import unittest

import arcproject.scripts.mapping
from arcproject.waterquality import classes

import arcpy

class TestWQToolBase(unittest.TestCase):

	def test_base_tool_date_retrieval(self):
		mb = arcproject.scripts.mapping.WQMappingBase

		base_class = mb()