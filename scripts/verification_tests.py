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
		verify.verify_summary_file(1, 2013, s)

	def test_dec_2013(self):
		s = os.path.join(test_data, r"Dec_2013\SummaryFiles\Dec2013_GPS\StatePlaneCAII\Arc_Dec2013_WQt_w_finalchl.shp")
		verify.verify_summary_file(12, 2013, s)
