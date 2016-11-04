import unittest
from scripts import chl_reg
import pandas as pd

class ChlRegression(unittest.TestCase):

	def setUp(self):
		self.chl_gain = pd.DataFrame([['2014-11-03', 'BR1', 'gn1', 2.143636363636364],
		                         ['2014-11-03', 'BR1', 'gn10', 2.732857142857143],
		                         ['2014-11-03', 'BR1', 'gn100', 2.7260000000000004],
		                         ['2014-11-03', 'BR2', 'gn1', 0.9875],
		                         ['2014-11-03', 'BR2', 'gn10', 1.36375],
		                         ['2014-11-03', 'BR2', 'gn100', 1.3840000000000001],
		                         ['2014-11-03', 'SI1', 'gn1', 1.2345454545454544],
		                         ['2014-11-03', 'SI1', 'gn10', 1.3279999999999998],
		                         ['2014-11-03', 'SI1', 'gn100', 1.4324999999999999],
		                         ['2014-11-03', 'SI2', 'gn1', 0.7260000000000002],
		                         ['2014-11-03', 'SI2', 'gn10', 1.377777777777778],
		                         ['2014-11-03', 'SI2', 'gn100', 1.3600000000000003],
		                         ['2014-11-03', 'SI4', 'gn1', 0.6859999999999999],
		                         ['2014-11-03', 'SI4', 'gn10', 1.005],
		                         ['2014-11-03', 'SI4', 'gn100', 1.011],
		                         ['2014-11-03', 'SI6', 'gn1', 0.8763636363636365],
		                         ['2014-11-03', 'SI6', 'gn10', 27.677999999999997],
		                         ['2014-11-03', 'SI6', 'gn100', 1.376],
		                         ['2014-11-03', 'SI7', 'gn1', 0.7437499999999999],
		                         ['2014-11-03', 'SI7', 'gn10', 1.3854545454545453],
		                         ['2014-11-03', 'SI7', 'gn100', 1.1155555555555556]],
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

	def test_Chl_eq(self):
		#self.assertEqual(cdt.chl_correction(self.raw, self.a, self.b), 16.23)
		pass


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

if __name__ == '__main__':
	unittest.main()
