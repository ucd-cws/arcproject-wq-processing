import unittest
import os
from datetime import datetime
from wq_gps_match import timestamp_match
import pandas


class LoadWQ(unittest.TestCase):

	def setUp(self):
		self.data = os.path.join("examples", "Arc_040413_WQ", "Arc_040413_wqt_bk.csv")
		pass

	def test_data_headers(self):
		self.assertEqual(
			list(timestamp_match.wq_from_csv(self.data).columns.values),
			['Date_Time', 'Temp', 'pH', 'SpCond', 'DO%', 'DO', 'DEP25', 'PAR', 'RPAR', 'TurbSC', 'CHL', 'CHL.1'])

	def test_data_length(self):
		self.assertEqual(timestamp_match.wq_from_csv(self.data).shape, (2128, 12))


class LoadSHP(unittest.TestCase):

	def setUp(self):
		self.data = os.path.join("examples", "Arc_040413_GPS", "040413_PosnPnt.shp")
		pass

	def test_length(self):
		self.assertEqual(timestamp_match.shp2dataframe(self.data).shape, (15976, 2))


class CheckDates(unittest.TestCase):

	def setUp(self):
		self.date = [2013, 4, 4]
		self.time = '08:18:47am'
		self.date_time = timestamp_match.TimestampFromDateTime(self.date, self.time)
		pass

	def test_ISO8601(self):
		self.assertEqual(self.date_time.strftime("%Y-%m-%dT%H:%M:%S"), self.date_time.isoformat())

	def test_DST(self):
		# make example date time into a dataframe with "Date_Time"
		self.df = pandas.DataFrame({'Date_Time': [self.date_time]})

		# add/subtract an hour
		self.plus1 = timestamp_match.dstadjustment(self.df, 1)
		self.minus1 = timestamp_match.dstadjustment(self.df, -1)

		# get first row
		self.plus1hr = self.plus1.loc[0]['Date_Time']
		self.minus1hr = self.minus1.loc[0]['Date_Time']

		# test against string
		self.assertEqual(self.plus1hr, datetime.strptime('2013-04-04 09:18:47', '%Y-%m-%d %H:%M:%S'))
		self.assertEqual(self.minus1hr, datetime.strptime('2013-04-04 07:18:47', '%Y-%m-%d %H:%M:%S'))

class CheckJoin(unittest.TestCase):

	def setUp(self):
		self.data = os.path.join("examples", "Arc_040413_GPS", "040413_PosnPnt.shp")
		pass


if __name__ == '__main__':
	unittest.main()
