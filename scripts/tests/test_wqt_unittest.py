import os
import unittest
from datetime import datetime
import pandas

from scripts import wqt_timestamp_match
from waterquality import classes

from sqlalchemy.orm.exc import NoResultFound


class TestDBInsert(unittest.TestCase):

	def setUp(self):
		self.data = os.path.join("testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqt_cc.csv")
		self.site_code = "wqt"
		self.session = classes.get_new_session()
		self._make_site()

	def _make_site(self):
		"""
			When testing on test server, database will be cleaned first, but when DB exists, we'll need to check if the site
			exists, and only create it when it doesn't exist
		:return:
		"""

		if self.session.query(classes.Site).filter(classes.Site.code == self.site_code).one_or_none() is None:
			new_site = classes.Site()
			new_site.code = self.site_code
			new_site.name = "Testing Site"
			self.session.add(new_site)
			self.session.commit()

	def test_data_insert(self):
		matched = wqt_timestamp_match.wq_from_file(self.data)
		wqt_timestamp_match.wq_df2database(matched, session=self.session)

		expected = len(matched)
		added = len(self.session.new)
		self.session.commit()
		self.session.close()
		self.assertEqual(expected, added)  # assert at end so that database commit occurs and we can inspect

	def test_records_in_db(self):
		num_records = self.session.query(classes.WaterQuality.id).filter(classes.Site.code == self.site_code).count()

		self.assertEqual(977, num_records)

class LoadWQ(unittest.TestCase):

	def setUp(self):
		self.data = os.path.join("testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqt_cc.csv")

	def test_data_headers(self):
		headers = wqt_timestamp_match.wq_from_file(self.data).columns.values

		for head in headers:
			self.assertIn(head, ['Date_Time', 'Temp', 'pH', 'SpCond', 'DO%', 'DO', 'DEP25',
			                     'PAR', 'RPAR', 'TurbSC', 'CHL', 'CHL_VOLTS', 'Sal', 'WQ_SOURCE'])

	def test_data_length(self):
		self.assertEqual(wqt_timestamp_match.wq_from_file(self.data).shape, (977, 12))


class LoadSHP(unittest.TestCase):
	"""
		Requires ArcGIS 10.4 or Pro 1.3 or above because we need datetimes in numpy arrays
	"""

	def setUp(self):
		self.data = os.path.join("testfiles", "Arc_040413", "Arc_040413_GPS", "040413_PosnPnt.shp")
		self.shpdf = wqt_timestamp_match.wqtshp2pd(self.data)
		pass

	def test_length(self):
		self.assertEqual(self.shpdf.shape, (15976, 6))

	def test_headers(self):
		headers = self.shpdf.columns.values
		for head in headers:
			self.assertIn(head, ['Date_Time', 'GPS_SOURCE', 'GPS_Date', 'GPS_Time', 'POINT_X', 'POINT_Y'])

class CheckDates(unittest.TestCase):

	def setUp(self):
		self.date = '2013-4-4'
		self.time = '08:18:47am'
		self.date_time = wqt_timestamp_match.TimestampFromDateTime(self.date, self.time)
		pass

	def test_ISO8601(self):
		self.assertEqual(self.date_time.strftime("%Y-%m-%dT%H:%M:%S"), self.date_time.isoformat())

	def test_DST(self):
		# make example date time into a dataframe with "Date_Time"
		self.df = pandas.DataFrame({'Date_Time': [self.date_time]})

		# add/subtract an hour
		self.plus1 = wqt_timestamp_match.dstadjustment(self.df, 1)
		self.minus1 = wqt_timestamp_match.dstadjustment(self.df, -1)

		# get first row
		self.plus1hr = self.plus1.loc[0]['Date_Time']
		self.minus1hr = self.minus1.loc[0]['Date_Time']

		# test against string
		self.assertEqual(self.plus1hr, datetime.strptime('2013-04-04 09:18:47', '%Y-%m-%d %H:%M:%S'))
		self.assertEqual(self.minus1hr, datetime.strptime('2013-04-04 07:18:47', '%Y-%m-%d %H:%M:%S'))


class CheckJoin(unittest.TestCase):

	def setUp(self):
		self.wq = os.path.join("testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqt_cc.csv")
		self.gps = os.path.join("testfiles", "Arc_040413_GPS", "040413_PosnPnt.shp")

	def test_join(self):
		pass


if __name__ == '__main__':
	unittest.main()
