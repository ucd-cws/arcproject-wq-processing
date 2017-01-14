"""
	These are structured as unittests, but are not in the tests directory because they test the data in a way that
	shouldn't be automatically run. We will manually run this, and failure doesn't mean code is broken necessarily
"""

import unittest
import os
import datetime

from scripts import verify

test_data = r"C:\Users\dsx.AD3\Box Sync\arcproject"


class Test2013(unittest.TestCase):
	def test_jan_2013(self):
		d1 = datetime.datetime(2013,1,7)
		d2 = datetime.datetime(2013,1,10)
		d3 = datetime.datetime(2013,1,11)
		d4 = datetime.datetime(2013,1,18)
		s = os.path.join(test_data, r"Jan_2013\SummaryFiles\Jan2013_GPS\StatePlaneCAII")

		verify.verify_summary_file(s, [d1, d2, d3, d4])