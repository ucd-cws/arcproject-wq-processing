"""
	These are structured as unittests, but are not in the tests directory because they test the data in a way that
	shouldn't be automatically run. We will manually run this, and failure doesn't mean code is broken necessarily
"""

import unittest
import os

from scripts import verify

test_data = r"C:\Users\dsx.AD3\Box Sync\arcproject"


class Test2013(unittest.TestCase):
	def test_jan_2013(self):
		s = os.path.join(test_data, r"Jan_2013\SummaryFiles\Jan2013_GPS\StatePlaneCAII\Arc_Jan2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(1, 2013, s))

	def test_feb_2013(self):
		s = os.path.join(test_data, r"Feb_2013\SummaryFiles\Feb2013_GPS\StatePlaneCAII\Arc_Feb2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(2, 2013, s))

	def test_mar_2013(self):
		s = os.path.join(test_data, r"Mar_2013\SummaryFiles\Mar2013_GPS\StatePlaneCAII\Arc_Mar2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(3, 2013, s))

	def test_apr_2013(self):
		s = os.path.join(test_data, r"Apr_2013\SummaryFiles\Apr2013_GPS\StatePlaneCAII\Arc_Apr2013_WQ_Trans.shp")
		self.assertTrue(verify.verify_summary_file(4, 2013, s))

	def test_may_2013(self):
		s = os.path.join(test_data, r"May_2013\SummaryFiles\May2013_GPS\StatePlaneCAII\Arc_May2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(5, 2013, s))

	def test_jun_2013(self):
		s = os.path.join(test_data, r"Jun_2013\SummaryFiles\Jun2013_GPS\StatePlaneCAII\Arc_Jun2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(6, 2013, s))

	def test_jul_2013(self):
		s = os.path.join(test_data, r"Jul_2013\SummaryFiles\Jul2013_GPS\StatePlaneCAII\Arc_Jul2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(7, 2013, s))

	def test_aug_2013(self):
		s = os.path.join(test_data, r"Aug_2013\SummaryFiles\Aug2013_GPS\StatePlaneCAII\Arc_Aug2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(8, 2013, s))

	def test_sep_2013(self):
		s = os.path.join(test_data, r"Sep_2013\SummaryFiles\Sep2013_GPS\StatePlaneCAII\Arc_Sep2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(9, 2013, s))

	def test_oct_2013(self):
		s = os.path.join(test_data, r"Oct_2013\SummaryFiles\Oct2013_GPS\StatePlaneCAII\Arc_Oct2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(10, 2013, s))

	def test_nov_2013(self):
		s = os.path.join(test_data, r"Nov_2013\SummaryFiles\Nov2013_GPS\StatePlaneCAII\Arc_Nov2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(11, 2013, s))

	def test_dec_2013(self):
		s = os.path.join(test_data, r"Dec_2013\SummaryFiles\Dec2013_GPS\StatePlaneCAII\Arc_Dec2013_WQt_w_finalchl.shp")
		self.assertTrue(verify.verify_summary_file(12, 2013, s))
