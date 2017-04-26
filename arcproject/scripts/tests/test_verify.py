import os
import unittest
import shutil
import logging

log = logging.getLogger("arcproject_tests")

from arcproject.scripts import wqt_timestamp_match
from arcproject.scripts import verify
from scripts.exceptions import NoRecordsError
from arcproject.waterquality import utils
from arcproject.waterquality import classes

base_path = os.path.split(os.path.abspath(__file__))[0]

class TestVerify(unittest.TestCase):

	def setUp(self):
		self.dec_2013_summary_file = r"testfiles/Dec_2013/SummaryFiles/Dec2013_GPS/StatePlaneCAII/Arc_Dec2013_WQt_w_finalchl.shp"
		self.site_codes = ["hs1", "bk", "bk0", "cache", "hs2", "hs3", "ln", "ul", "ul0", "dv", "dv_1", "lc", "lc_2", "mz", "sb"]

		self.wq_12_11_files = ["Arc_121113_wqt_hs1", "Arc_121113_wqt_bk", "Arc_121113_wqt_bk0", "Arc_121113_wqt_cache",
								"Arc_121113_wqt_hs2", "Arc_121113_wqt_hs3", "Arc_121113_wqt_ln", "Arc_121113_wqt_ul", "Arc_121113_wqt_ul0"]
		self.wq_12_11_path = os.path.join("testfiles", "Dec_2013", "Arc_121113", "Arc_121113_WQ")
		self.wq_12_11 = [os.path.join(self.wq_12_11_path, filename) for filename in self.wq_12_11_files]
		self.wq_12_11_gps = os.path.join("testfiles", "Dec_2013", "Arc_121113", "Arc_121113_GPS", "121113_PosnPnt.shp")

		self.wq_12_13_files = ["Arc_121313_wqt_dv", "Arc_121313_wqt_dv_1", "Arc_121313_wqt_lc", "Arc_121313_wqt_lc_2",
							   "Arc_121313_wqt_mz", "Arc_121313_wqt_sb", ]
		self.wq_12_13_path = os.path.join("testfiles", "Dec_2013", "Arc_121313", "Arc_121313_WQ")
		self.wq_12_13 = [os.path.join(self.wq_12_13_path, filename) for filename in self.wq_12_13_files]
		self.wq_12_13_gps = os.path.join("testfiles", "Dec_2013", "Arc_121313", "Arc_121313_GPS", "121313_PosnPnt.shp")

	def _remake_db(self):
		"""
			Copies the db to a new spot, directs the software to use it, then empties the DB so that it's blank
		:return: 
		"""

		self.original_db = classes.db_location
		tmp_path = os.path.join(base_path, "test_tmp")
		self.new_db = os.path.join(tmp_path, "wqdb.sqlite")

		if not os.path.exists(tmp_path):  # make sure the folders exist
			os.makedirs(tmp_path)
		shutil.copyfile(self.original_db, self.new_db)  # then copy the db to it

		classes.db_location = self.new_db  # tell the software to use the new DB location

		utils.recreate_tables()  # recreate the table structure

		for site in self.site_codes:  # and add in the site codes specified
			self._make_site(site)

	def _restore_db(self):
		classes.db_location = self.original_db

		try:
			os.remove(self.new_db)
		except:
			log.warning("Couldn't delete temporary database - you may need to remove it manually")

	def _load_data(self, wq_files, gps_data):
		# add one set of records for Dec 2013
		for wq_file in wq_files:
			wqt_timestamp_match.main([wq_file], gps_data, site_func_params={"site_part": 3, "gain_part": 4}, dst_adjustment=True)

	def _make_site(self, site):

		self.session = classes.get_new_session()
		try:
			if self.session.query(classes.Site).filter(classes.Site.code == site).one_or_none() is None:
				new_site = classes.Site()
				new_site.code = site
				new_site.name = "Testing Site"
				self.session.add(new_site)
				self.session.commit()
		finally:
			self.session.close()

	def test_verify_basic_has_all_records(self):
		"""
			We should load all the data for the month into the database and then assert that it's all there.
		:return:
		"""
		self._remake_db()  # load all of the december data
		self._load_data(self.wq_12_11, self.wq_12_11_gps)
		self._load_data(self.wq_12_13, self.wq_12_13_gps)
		self.assertTrue(verify.verify_summary_file(12, 2013, self.dec_2013_summary_file, max_missing_points=15))
		# self.assertTrue(False)  # This test should be failing as constructed because not all data is loaded

		self._restore_db()

	def test_verify_fail_no_records_for_date(self):
		"""
			Checks that if we have no records in the database for a date, that the test raises NoRecordsError
		:return:
		"""
		self.assertRaises(NoRecordsError, verify.verify_summary_file, 1, 2010, self.dec_2013_summary_file)  # date that predates project

	def test_verify_missing_records(self):
		"""
			This test only loads some of the data for the month, but should then detect that records are missing
		:return:
		"""
		self._remake_db()
		self._load_data(self.wq_12_11, self.wq_12_11_gps)
		# run verification
		self.assertFalse(verify.verify_summary_file(12, 2013, self.dec_2013_summary_file, max_missing_points=15))
		self._restore_db()


