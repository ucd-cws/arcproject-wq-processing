import unittest

from scripts import verify
import datetime

class TestVerify(unittest.TestCase):
	def test_verify(self):
		d1 = datetime.datetime(2013,12,11)
		d2 = datetime.datetime(2013,12,13)
		s = r"C:\Users\dsx.AD3\Downloads\mybox-selected\Arc_Dec2013_WQt_w_finalchl.shp"

		verify.verify_summary_file(s, [d1,d2])