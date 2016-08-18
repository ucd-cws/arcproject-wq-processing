import unittest
import os
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


if __name__ == '__main__':
	unittest.main()
