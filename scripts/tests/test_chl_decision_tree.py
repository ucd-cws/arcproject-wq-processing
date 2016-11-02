import unittest
from scripts import chl_decision_tree as cdt
import pandas as pd

class ChlCorrection(unittest.TestCase):

	def setUp(self):
		self.a = 8.3
		self.b = 1.3
		self.raw = 6.1
		self.r2_sig = 0.9
		self.r2_nosig = 0.7
		pass

	def test_Chl_eq(self):
		self.assertEqual(cdt.chl_correction(self.raw, self.a, self.b), 16.23)
		pass

	def test_lm_sig(self):
		self.assertEqual(cdt.lm_significant(self.raw, self.r2_nosig, self.a, self.b), self.raw)
		self.assertEqual(cdt.lm_significant(self.raw, self.r2_sig, self.a, self.b), 16.23)
		pass

class LookupReg(unittest.TestCase):

	def setUp(self):
		self.df = pd.DataFrame([['2013-01-07', 'gn0', 0.999913452106, -0.7004800719059999, 0.911512370843],
                                ['2013-01-08', 'gn0', 0.712038046822, 0.353666429071, 0.190055423761],
                                ['2013-01-10', 'gn0', 0.175292257503, 2.31933396825, -1.0721551944],
                                ['2014-01-13', 'gn10', 0.987127460968, -1.77156121034, 1.01214030496],
                                ['2014-01-13', 'gn1', 0.8819283496979999, -2.19331177439, 1.7788943440599998]],
								columns=['Date', 'Gain', 'Rsquared', 'A_coeff', 'B_coeff'])
		pass

	def test_check_row_exists(self):
		self.assertFalse(cdt.check_gain_reg_exists(self.df, '2013-01-09', 'gn0'))
		self.assertFalse(cdt.check_gain_reg_exists(self.df, '2013-01-08', 'gn10'))
		self.assertTrue(cdt.check_gain_reg_exists(self.df, '2014-01-13', 'gn10'))
		pass

	def test_check_lookup(self):
		self.assertEqual(cdt.lookup_regression_values(self.df, '2013-01-08', 'gn0'),
		                 (0.712038046822, 0.35366642907099999, 0.19005542376099999))

		self.assertEqual(cdt.lookup_regression_values(self.df, '2014-01-13', 'gn1'),
		                 (0.8819283496979999, -2.19331177439, 1.7788943440599998))

		pass

	def test_chl_descision(self):
		self.assertEqual(cdt.chl_decision(10, self.df, '2013-01-07'), ?)
		self.assertEqual(cdt.chl_decision(10, self.df, '2013-01-08'), 10)
		self.assertEqual(cdt.chl_decision(4, self.df, '2014-01-13'), ?)
		self.assertEqual(cdt.chl_decision(10, self.df, '2014-01-13'), ?)
		self.assertEqual(cdt.chl_decision(50, self.df, '2014-01-13'), ?)


if __name__ == '__main__':
	unittest.main()
