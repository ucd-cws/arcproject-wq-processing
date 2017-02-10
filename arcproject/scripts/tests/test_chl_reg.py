import unittest
from arcproject.scripts import chl_reg
import pandas as pd

from arcproject.waterquality import shorten_float


class LinearRegression(unittest.TestCase):
	def setUp(self):
		self.x = [2, 4, 6, 8, 10]
		self.y = [1, 2, 3, 9, 9]
		self.z = [7, 11, 15, 19, 23]
		pass

	def test_Rsquared(self):
		self.assertEqual(chl_reg.get_r2_numpy(self.x, self.x), 1)
		self.assertEqual(chl_reg.get_r2_numpy(self.x, self.y), 0.87006578947368451)
		self.assertEqual(chl_reg.get_r2_numpy(self.x, self.z), 1)
		pass

	def test_LinearReg(self):
		self.assertAlmostEqual(chl_reg.linear_reg_numpy(self.x, self.y)[0], 1.149999999)
		self.assertAlmostEqual(chl_reg.linear_reg_numpy(self.x, self.y)[1], -2.0999999999)
		self.assertAlmostEqual(chl_reg.linear_reg_numpy(self.x, self.z)[0], 2)
		self.assertAlmostEqual(chl_reg.linear_reg_numpy(self.x, self.z)[1], 3)
		pass


class ChlRegression(unittest.TestCase):

	def setUp(self):
		self.chl_gain = pd.DataFrame([['2014-11-03', 'BR1', 1, 2.143636363636364],
		                         ['2014-11-03', 'BR1', 10, 2.732857142857143],
		                         ['2014-11-03', 'BR1', 100, 2.7260000000000004],
		                         ['2014-11-03', 'BR2', 1, 0.9875],
		                         ['2014-11-03', 'BR2', 10, 1.36375],
		                         ['2014-11-03', 'BR2', 100, 1.3840000000000001],
		                         ['2014-11-03', 'SI1', 1, 1.2345454545454544],
		                         ['2014-11-03', 'SI1', 10, 1.3279999999999998],
		                         ['2014-11-03', 'SI1', 100, 1.4324999999999999],
		                         ['2014-11-03', 'SI2', 1, 0.7260000000000002],
		                         ['2014-11-03', 'SI2', 10, 1.377777777777778],
		                         ['2014-11-03', 'SI2', 100, 1.3600000000000003],
		                         ['2014-11-03', 'SI4', 1, 0.6859999999999999],
		                         ['2014-11-03', 'SI4', 10, 1.005],
		                         ['2014-11-03', 'SI4', 100, 1.011],
		                         ['2014-11-03', 'SI6', 1, 0.8763636363636365],
		                         ['2014-11-03', 'SI6', 10, 27.677999999999997],
		                         ['2014-11-03', 'SI6', 100, 1.376],
		                         ['2014-11-03', 'SI7', 1, 0.7437499999999999],
		                         ['2014-11-03', 'SI7', 10, 1.3854545454545453],
		                         ['2014-11-03', 'SI7', 100, 1.1155555555555556]],
		                        columns=['Date', 'Site', 'Gain', 'Chl'])

		self.chl_lab = pd.DataFrame(	[['2014-11-03', 'BR1', 1.7],
										['2014-11-03', 'BR2', 1.3],
										['2014-11-03', 'SI6', 1.1],
										['2014-11-03', 'SI7', 0.9],
										['2014-11-03', 'SI1', 2],
										['2014-11-03', 'SI2', 1.5],
										['2014-11-03', 'SI4', 1.1]
										], columns=['Date', 'SiteID', 'ChlA'])
		pass

	def test_Main(self):
		self.assertAlmostEqual(chl_reg.main(self.chl_gain, self.chl_lab, 100)[0], 0.28082684720720524)
		self.assertAlmostEqual(chl_reg.main(self.chl_gain, self.chl_lab, 100)[1], 0.83684782181753625)
		self.assertAlmostEqual(chl_reg.main(self.chl_gain, self.chl_lab, 100)[2], 0.35963914150167603)

		# Example for viewing scatter (not a test)
		#chl_reg.main(self.chl_gain, self.chl_lab, "gn1", view_scatter=True)

		pass

if __name__ == '__main__':
	unittest.main()
