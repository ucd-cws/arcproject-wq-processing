import unittest
import pandas as pd
import six

from sqlalchemy.exc import IntegrityError

from scripts import chl_decision_tree as cdt
from waterquality import classes


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
		self.df = pd.DataFrame([['2013-01-07', 'g0', 0.999913452106, -0.7004800719059999, 0.911512370843],
                                ['2013-01-08', 'g0', 0.712038046822, 0.353666429071, 0.190055423761],
                                ['2013-01-10', 'g0', 0.175292257503, 2.31933396825, -1.0721551944],
                                ['2014-01-13', 'g10', 0.987127460968, -1.77156121034, 1.01214030496],
                                ['2014-01-13', 'g1', 0.8819283496979999, -2.19331177439, 1.7788943440599998],
                                ['2014-01-13', 'g100', 0.8819283496979999, -2.19331177439, 1.7788943440599998],
                                ['2014-11-13', 'g10', 0.7, -1.77156121034, 1.01214030496],
                                ['2014-11-13', 'g1', 0.1, -2.19331177439, 1.7788943440599998],
                                ['2014-11-13', 'g100', 0.79, -2.19331177439, 1.7788943440599998]
		                        ],
								columns=['Date', 'Gain', 'Rsquared', 'A_coeff', 'B_coeff'])

		try:
			cdt.load_regression_data(self.df)
		except IntegrityError:
			pass  # it's probably OK in this case - it should mean the data is already there - tests will fail later if it isn't

	def test_check_row_exists(self):

		session = classes.get_new_session()
		try:
			self.assertFalse(cdt.check_gain_reg_exists(session, '2013-01-09', 'g0'))
			self.assertFalse(cdt.check_gain_reg_exists(session, '2013-01-08', 'g10'))
			self.assertTrue(cdt.check_gain_reg_exists(session, '2014-01-13', 'g10'))
		finally:
			session.close()

	def test_check_lookup(self):
		session = classes.get_new_session()

		try:
			self.assertEqual(cdt.lookup_regression_values(self.df, '2013-01-08', 'g0'),
							 (0.712038046822, 0.35366642907099999, 0.19005542376099999))

			self.assertEqual(cdt.lookup_regression_values(self.df, '2014-01-13', 'g1'),
							 (0.8819283496979999, -2.19331177439, 1.7788943440599998))
		finally:
			session.close()

	def shorten_float(self, original, places=8):
		"""
		Used in order to make floats a consistent length for unit tests - it's OK to shorten them because with 8
		decimal places we should be able to test if the code is functioning correctly. Beyond that the small specifics probably
		aren't super important
		:param original: The original number
		:param places: The number of decimal places to shorten it to (obeys rounding rules)
		:return: new number with specified number of decimal places
		"""
		format_str = "{0:." + six.text_type(places) + "f}"
		return float(format_str.format(original))

	def test_chl_descision(self):
		# g0 sig
		self.assertEqual(self.shorten_float(cdt.chl_decision(10, '2013-01-07')), 8.41464364)
		# g0 nosig
		self.assertEqual(cdt.chl_decision(10, '2013-01-08'), 10)
		# g100 sig
		self.assertEqual(self.shorten_float(cdt.chl_decision(4, '2014-01-13')), 4.92226560)
		# g10 sig
		self.assertEqual(self.shorten_float(cdt.chl_decision(10, '2014-01-13')), 8.34984184)
		# g1 sig
		self.assertEqual(self.shorten_float(cdt.chl_decision(50, '2014-01-13')), 86.75140543)
		# g100 no sig
		self.assertEqual(cdt.chl_decision(4, '2014-11-13'), 4)
		# g10 no sig
		self.assertEqual(cdt.chl_decision(10, '2014-11-13'), 10)
		# g1 no sig
		self.assertEqual(cdt.chl_decision(50, '2014-11-13'), 50)

if __name__ == '__main__':
	unittest.main()
