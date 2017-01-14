import unittest

from scripts import verify
import datetime

class TestVerify(unittest.TestCase):
	def test_verify(self):
		s = r"C:\Users\dsx.AD3\Downloads\mybox-selected\Arc_Dec2013_WQt_w_finalchl.shp"
		verify.verify_summary_file(1, 2013, s)