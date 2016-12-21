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
		self.gps = os.path.join("testfiles", r"Arc_040413\Arc_040413_GPS\040413_ZoopChlW.shp")
		self.gain_data = wq_gain.convert_wq_dtypes(wqt_timestamp_match.wq_from_file(self.data))
		self.depth_field = "DEP25"
		pass

	def test_data_headers(self):
		headers = wqt_timestamp_match.wq_from_file(self.data).columns.values

		for head in headers:
			self.assertIn(head, ['Date_Time', 'Temp', 'pH', 'SpCond', 'DO%', 'DO', 'DEP25',
			                     'PAR', 'RPAR', 'TurbSC', 'CHL', 'CHL_VOLTS', 'Sal', 'WQ_SOURCE'])
		pass

	def test_filterTopMeter(self):
		# there should only be records between 0 and 1m
		one_meter = wq_gain.depth_top_meter(self.gain_data, self.depth_field)

		max_value = max(one_meter[self.depth_field])
		min_value = min(one_meter[self.depth_field])

		self.assertLessEqual(max_value, 1)
		self.assertGreaterEqual(min_value, 0)

	def test_df_len(self):
		self.assertEqual(self.gain_data, (75, 12))

		# there should be 13 records between 0 and 1m
		one_meter = wq_gain.depth_top_meter(self.gain_data, self.depth_field)
		self.assertEqual(one_meter.shape, (13, 12))

		# taking the average should result in just one record
		avg_meter = wq_gain.avg_vert_profile(one_meter)
		self.assertEqual(avg_meter.shape, (1, 10))

		pass

	def test_df_type(self):
		# test that the type is a pandas dataframe
		df = type(pandas.DataFrame())
		self.assertIsInstance(self.gain_data, df)

		one_meter = wq_gain.depth_top_meter(self.gain_data, self.depth_field)
		self.assertIsInstance(one_meter, df)

		avg_meter = wq_gain.avg_vert_profile(one_meter)
		self.assertIsInstance(avg_meter, df)

	def test_JoinwGPS(self):

		# get the average for the top 1m of the gain
		one_meter = wq_gain.depth_top_meter(self.gain_data, self.depth_field)
		avg_meter = wq_gain.avg_vert_profile(one_meter)

		# add the site code to the gain file
		avg_meter['Site'] = "CC1"

		# load the shp attributes as a pd df
		gps_df = wqt_timestamp_match.wqtshp2pd(self.gps)

		# join using the site code
		join = wq_gain.gain_join_gps_by_site(avg_meter, gps_df)

		# assert that the join was successful by checking the expected dimensions
		self.assertEqual(join.shape, (1, 26))

		# check that the df has columns named POINT_Y and POINT_X
		headers = join.columns.values
		self.assertIn("POINT_X", headers)
		self.assertIn("POINT_Y", headers)
		pass


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


class ParseSiteGain(unittest.TestCase):
	def setUp(self):
		self.ex1 = 'ARC_202020_bk1_gn1'
		self.ex2 = 'ARC_g1_111111_junk_bk1'
		pass

	def test_parse_site(self):
		self.assertEqual(wq_gain.profile_function_historic(filename=self.ex1, part=2), "BK1")
		self.assertEqual(wq_gain.profile_function_historic(filename=self.ex2, part=1), "G1")
		self.assertEqual(wq_gain.profile_function_historic(filename=self.ex2, part=4), "BK1")

if __name__ == '__main__':
	unittest.main()
