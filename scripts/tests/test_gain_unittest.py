import os
import unittest
from datetime import datetime
from scripts import wq_gain
from scripts import wqt_timestamp_match
import pandas
from pandas.util.testing import assert_frame_equal

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

	def test_df_type(self):
		# test that the type is a pandas dataframe
		df = type(pandas.DataFrame())
		self.assertIsInstance(self.top1m, df)

		one_meter = wq_gain.depth_top_meter(self.top1m, "DEP25")
		self.assertIsInstance(one_meter, df)

		avg_meter = wq_gain.avg_vert_profile(one_meter)
		self.assertIsInstance(avg_meter, df)

class ConvertType(unittest.TestCase):
	# tests for convert dtypes in gain files

	def setUp(self):
		self.df_w_obj = pandas.DataFrame({'a': pandas.Series(['1.1', '2.2', '3.3'], dtype=object),
		                                  'b': pandas.Series(["Z", "Y", "X"], dtype=str),
		                                  'c': pandas.Series(['2011-01-01 00:00:00', '2011-02-01 00:00:00',
		                                                      '2011-03-01 00:00:00'], dtype='datetime64[ns]')})

		self.df_w_num = pandas.DataFrame({'a': pandas.Series([1.1, 2.2, 3.3], dtype=float),
		                                  'b': pandas.Series(["Z", "Y", "X"], dtype=str),
		                                  'c': pandas.Series(['2011-01-01 00:00:00', '2011-02-01 00:00:00',
		                                                      '2011-03-01 00:00:00'], dtype='datetime64[ns]')})
		pass

	def test_convert_str2num(self):

		# get data types before running the function
		df_w_obj_dtype = self.df_w_obj.dtypes.tolist()
		df_w_n_dtype = self.df_w_num.dtypes.tolist()

		#  try to convert all dtype "objects" into numbers
		converted = wq_gain.convert_wq_dtypes(self.df_w_obj)

		# get data types as a list
		converted_dtype = converted.dtypes.tolist()

		self.assertEqual(converted_dtype, df_w_n_dtype)
		self.assertNotEqual(converted_dtype, df_w_obj_dtype)

	pass

if __name__ == '__main__':
	unittest.main()
