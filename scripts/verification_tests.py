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
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(1, 2013, s))

	def test_feb_2013(self):
		s = os.path.join(test_data, r"Feb_2013\SummaryFiles\Feb2013_GPS\StatePlaneCAII\Arc_Feb2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(2, 2013, s))

	def test_mar_2013(self):
		s = os.path.join(test_data, r"Mar_2013\SummaryFiles\Arc_Mar2013_GPS\StatePlaneCAII\Arc_Mar2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(3, 2013, s))

	def test_apr_2013(self):
		s = os.path.join(test_data, r"Apr_2013\SummaryFiles\Apr2013_GPS\StatePlaneCAII\Arc_Apr2013_WQt.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(4, 2013, s))

	def test_may_2013(self):
		s = os.path.join(test_data, r"May_2013\SummaryFiles\May2013_GPS\StatePlaneCAII\Arc_May2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(5, 2013, s))

	def test_jun_2013(self):
		s = os.path.join(test_data, r"Jun_2013\SummaryFiles\Arc_Jun2013_GPS\StatePlaneCAII\Arc_Jun2013_WQt.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(6, 2013, s))

	def test_jul_2013(self):
		s = os.path.join(test_data, r"Jul_2013\SummaryFiles\Jul2013_GPS\StatePlaneCAII\Arc_Jul2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(7, 2013, s))

	def test_aug_2013(self):
		s = os.path.join(test_data, r"Aug_2013\SummaryFiles\Aug2013_GPS\StatePlaneCAII\Arc_Aug2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(8, 2013, s))

	def test_sep_2013(self):
		s = os.path.join(test_data, r"Sep_2013\SummaryFiles\Sep2013_GPS\StatePlaneCAII\Arc_Sep2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(9, 2013, s))

	def test_oct_2013(self):
		s = os.path.join(test_data, r"Oct_2013\SummaryFiles\Oct2013_GPS\StatePlaneCAII\Arc_Oct2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(10, 2013, s))

	def test_nov_2013(self):
		s = os.path.join(test_data, r"Nov_2013\SummaryFiles\Nov2013_GPS\StatePlaneCAII\Arc_Nov2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(11, 2013, s))

	def test_dec_2013(self):
		s = os.path.join(test_data, r"Dec_2013\SummaryFiles\Dec2013_GPS\StatePlaneCAII\Arc_Dec2013_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(12, 2013, s))


class Test2014(unittest.TestCase):
	def test_jan_2014(self):
		s = os.path.join(test_data, r"Jan_2014\SummaryFiles\Jan2014_GPS\StatePlaneCAII\Arc_Jan2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(1, 2014, s))

	def test_feb_2014(self):
		s = os.path.join(test_data, r"Feb_2014\SummaryFiles\Feb2014_GPS\StatePlaneCAII\Arc_Feb2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(2, 2014, s))

	def test_mar_2014(self):
		s = os.path.join(test_data, r"Mar_2014\SummaryFiles\Mar2014_GPS\StatePlaneCAII\Arc_Mar2014_WQt_w_final.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(3, 2014, s))

	def test_apr_2014(self):
		s = os.path.join(test_data, r"Apr_2014\SummaryFiles\Apr2014_GPS\StatePlaneCAII\Arc_Apr2014_WQt.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(4, 2014, s))

	def test_may_2014(self):
		s = os.path.join(test_data, r"May_2014\SummaryFiles\May2014_GPS\StatePlaneCAII\Arc_May2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(5, 2014, s))

	def test_jun_2014(self):
		s = os.path.join(test_data, r"Jun_2014\SummaryFiles\Jun2014_GPS\StatePlaneCAII\Arc_Jun2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(6, 2014, s))

	def test_jul_2014(self):
		s = os.path.join(test_data, r"Jul_2014\SummaryFiles\Jul2014_GPS\StatePlaneCAII\Arc_Jul2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(7, 2014, s))

	def test_aug_2014(self):
		s = os.path.join(test_data, r"Aug_2014\SummaryFiles\Aug2014_GPS\StatePlaneCAII\Arc_Aug2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(8, 2014, s))

	def test_sep_2014(self):
		s = os.path.join(test_data, r"Sep_2014\SummaryFiles\Sep2014_GPS\StatePlaneCAII\Arc_Sep2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(9, 2014, s))

	def test_oct_2014(self):
		s = os.path.join(test_data, r"Oct_2014\SummaryFiles\Oct2014_GPS\StatePlaneCAII\Arc_Oct2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(10, 2014, s))

	def test_nov_2014(self):
		s = os.path.join(test_data, r"Nov_2014\SummaryFiles\Nov2014_GPS\StatePlaneCAII\Arc_Nov2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(11, 2014, s))

	def test_dec_2014(self):
		s = os.path.join(test_data, r"Dec_2014\SummaryFiles\Dec2014_GPS\StatePlaneCAII\Arc_Dec2014_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(12, 2014, s))


class Test2015(unittest.TestCase):

	def test_apr_2015(self):
		s = os.path.join(test_data, r"Apr_2015\SummaryFiles\Apr2015_GPS\StatePlaneCAII\Arc_Apr2015_WQ_Trans.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(4, 2015, s))

	def test_may_2015(self):
		s = os.path.join(test_data, r"May_2015\SummaryFiles\May2015_GPS\StatePlaneCAII\Arc_May2015_WQt.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(5, 2015, s))

	def test_jun_2015(self):
		s = os.path.join(test_data, r"Jun_2015\SummaryFiles\June15_WQT.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(6, 2015, s))

	def test_jul_2015(self):
		s = os.path.join(test_data, r"Jul_2015\SummaryFiles\ARC_Jul15_WQT.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(7, 2015, s))

	def test_aug_2015(self):
		s = os.path.join(test_data, r"Aug_2015\SummaryFiles\Arc_Aug15_WQT.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(8, 2015, s))

	def test_sep_2015(self):
		s = os.path.join(test_data, r"Sep_2015\SummaryFiles\Arc_Sep15_WQT.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(9, 2015, s))

	def test_oct_2015(self):
		s = os.path.join(test_data, r"Oct_2015\SummaryFiles\Arc_Oct15_WQT.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(10, 2015, s))

	def test_nov_2015(self):
		s = os.path.join(test_data, r"Nov_2015\SummaryFiles\Arc_Nov15_WQT.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(11, 2015, s))

	def test_dec_2015(self):
		s = os.path.join(test_data, r"Dec_2015\SummaryFiles\Arc_Dec15_WQT.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(12, 2015, s))


class Test2016(unittest.TestCase):
	def test_jan_2016(self):
		s = os.path.join(test_data, r"Jan_2016\SummaryFiles\Jan2016_GPS\StatePlaneCAII\Arc_Jan2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(1, 2016, s))

	def test_feb_2016(self):
		s = os.path.join(test_data, r"Feb_2016\SummaryFiles\Feb2016_GPS\StatePlaneCAII\Arc_Feb2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(2, 2016, s))

	def test_mar_2016(self):
		s = os.path.join(test_data, r"Mar_2016\SummaryFiles\Mar2016_GPS\StatePlaneCAII\Arc_Mar2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(3, 2016, s))

	def test_apr_2016(self):
		s = os.path.join(test_data, r"Apr_2016\SummaryFiles\Apr2016_GPS\StatePlaneCAII\Arc_Apr2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(4, 2016, s))

	def test_may_2016(self):
		s = os.path.join(test_data, r"May_2016\SummaryFiles\May2016_GPS\StatePlaneCAII\Arc_May2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(5, 2016, s))

	def test_jun_2016(self):
		s = os.path.join(test_data, r"Jun_2016\SummaryFiles\Jun2016_GPS\StatePlaneCAII\Arc_Jun2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(6, 2016, s))

	def test_jul_2016(self):
		s = os.path.join(test_data, r"Jul_2016\SummaryFiles\Jul2016_GPS\StatePlaneCAII\Arc_Jul2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(7, 2016, s))

	def test_aug_2016(self):
		s = os.path.join(test_data, r"Aug_2016\SummaryFiles\Aug2016_GPS\StatePlaneCAII\Arc_Aug2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(8, 2016, s))

	def test_sep_2016(self):
		s = os.path.join(test_data, r"Sep_2016\SummaryFiles\Sep2016_GPS\StatePlaneCAII\Arc_Sep2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(9, 2016, s))

	def test_oct_2016(self):
		s = os.path.join(test_data, r"Oct_2016\SummaryFiles\Oct2016_GPS\StatePlaneCAII\Arc_Oct2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(10, 2016, s))

	def test_nov_2016(self):
		s = os.path.join(test_data, r"Nov_2016\SummaryFiles\Nov2016_GPS\StatePlaneCAII\Arc_Nov2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(11, 2016, s))

	def test_dec_2016(self):
		s = os.path.join(test_data, r"Dec_2016\SummaryFiles\Dec2016_GPS\StatePlaneCAII\Arc_Dec2016_WQt_w_finalchl.shp")
		self.assertTrue(os.path.exists(s))
		self.assertTrue(verify.verify_summary_file(12, 2016, s))