import unittest
import os
from datetime import datetime
from wq_gps_match import timestamp_match


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
		self.shp = os.path.join("examples", "Arc_040413_GPS", "040413_PosnPnt.shp")
		self.csv = os.path.join("examples", "Arc_040413_WQ", "Arc_040413_wqt_bk.csv")
		self.shpdates = timestamp_match.shp2dataframe(self.shp)["Date"].tolist()
		self.csvdates = timestamp_match.wq_from_csv(self.csv)["Date_Time"].tolist()
		pass

	def test_shp_ISO8601(self):
		for dt in self.shpdates:
			self.assertEqual(dt.strftime("%Y-%m-%dT%H:%M:%S"), dt.isoformat())

	def test_csv_ISO8601(self):
		for dt in self.csvdates:
			self.assertEqual(dt.strftime("%Y-%m-%dT%H:%M:%S"), dt.isoformat())


class CheckJoin(unittest.TestCase):

	def setUp(self):
		self.data = os.path.join("examples", "Arc_040413_GPS", "040413_PosnPnt.shp")
		pass


if __name__ == '__main__':
	unittest.main()
