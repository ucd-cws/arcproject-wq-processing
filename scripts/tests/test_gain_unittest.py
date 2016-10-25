import os
import unittest
from datetime import datetime
from scripts import wq_gain
from scripts import wqt_timestamp_match
import pandas


class LoadGainWQ(unittest.TestCase):

	def setUp(self):
		self.data = os.path.join("testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqp_ca3.csv")
		self.top1m = wq_gain.convert_wq_dtypes(wqt_timestamp_match.wq_from_file(self.data))
		pass

	def test_data_headers(self):
		headers = wqt_timestamp_match.wq_from_file(self.data).columns.values

		for head in headers:
			self.assertIn(head, ['Date_Time', 'Temp', 'pH', 'SpCond', 'DO%', 'DO', 'DEP25',
			                     'PAR', 'RPAR', 'TurbSC', 'CHL', 'CHL_VOLTS', 'Sal', 'WQ_SOURCE'])
		pass

	def test_df_len(self):
		self.assertEqual(wqt_timestamp_match.wq_from_file(self.data).shape, (75, 12))

		one_meter = wq_gain.depth_top_meter(self.top1m, "DEP25")
		self.assertEqual(one_meter.shape, (13, 12))

		avg_meter = wq_gain.avg_vert_profile(one_meter)
		self.assertEqual(avg_meter.shape, (1, 10))

		pass


if __name__ == '__main__':
	unittest.main()
