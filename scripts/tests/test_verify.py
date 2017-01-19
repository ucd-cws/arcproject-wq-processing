import os
import unittest

from scripts import wqt_timestamp_match
from scripts import verify
from scripts import NoRecordsError
from waterquality import utils
from waterquality import classes

class TestVerify(unittest.TestCase):

	def setUp(self):
		self.dec_2013 = r"testfiles/Dec_2013/SummaryFiles/Dec2013_GPS/StatePlaneCAII/Arc_Dec2013_WQt_w_finalchl.shp"
		self.site_code = "hs1"

		self.wq = os.path.join("testfiles", "Dec_2013", "Arc_121113", "Arc_121113_WQ", "Arc_121113_wqt_hs1")
		self.gps = os.path.join("testfiles", "Dec_2013", "Arc_121113", "Arc_121113_GPS", "121113_PosnPnt.shp")

	def _remake_db(self, wq_files=[self.wq, ]):
		print("Warning! Recreating Database!")
		utils.recreate_tables()

		self._make_site()

		# add one set of records for Dec 2013
		wqt_timestamp_match.main(wq_files, self.gps, site_func_params={"site_part": 3, "gain_part": 4})

	def _make_site(self):

		self.session = classes.get_new_session()
		try:
			if self.session.query(classes.Site).filter(classes.Site.code == self.site_code).one_or_none() is None:
				new_site = classes.Site()
				new_site.code = self.site_code
				new_site.name = "Testing Site"
				self.session.add(new_site)
				self.session.commit()
		finally:
			self.session.close()

	def test_verify_basic_has_all_records(self):

		self._remake_db()
		self.assertTrue(verify.verify_summary_file(12, 2013, self.dec_2013))
		self.assertTrue(False)  # This should be failing as constructed

	def test_verify_fail_no_records_for_date(self):
		self.assertRaises(NoRecordsError, verify.verify_summary_file, 1, 2010, self.dec_2013)  # date that predates project

	def test_verify_missing_records(self):

		self._remake_db()
		# run verification
		self.assertFalse(verify.verify_summary_file(12, 2013, self.dec_2013))


