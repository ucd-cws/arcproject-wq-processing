import unittest

from arcproject.waterquality import api
import datetime

import arcpy

class GetWQTest(unittest.TestCase):
	def test_data_retrieval(self):
		d1 = datetime.datetime(2013, 4, 4)
		api.get_wq_for_date(d1)