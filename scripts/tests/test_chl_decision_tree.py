import unittest
import pandas as pd
import os

from sqlalchemy.exc import IntegrityError

from scripts import chl_decision_tree as cdt
from waterquality import classes, shorten_float


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


class RegressionTable(unittest.TestCase):
	def setUp(self):
		file_path = os.path.abspath(os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, os.pardir))
		self.regression_data = os.path.join(file_path, "data", "legacy", "lm_coeffs_rsquared", "legacy_coeffs_rsquared.csv")

	def test_load_regression_data(self):
		try:
			cdt.load_regression_data_from_csv(self.regression_data)
		except IntegrityError:
			pass  # it's ok because data already loaded

		data = pd.read_csv(self.regression_data)

		session = classes.get_new_session()

		reg = classes.Regression
		try:
			for record in data.iterrows():
				record = record[1]
				self.assertTrue(session.query(classes.Regression)\
										.filter(reg.a_coefficient == shorten_float(record.A_coeff),
												reg.b_coefficient == shorten_float(record.B_coeff),
												reg.r_squared == shorten_float(record.Rsquared),
												reg.gain == record.Gain)\
										.count() > 0
								)

		finally:
			session.close()


class LookupReg(unittest.TestCase):

	def setUp(self):
		# this is fake data - should not be imported to database
		self.df = pd.DataFrame(
		                       [
			                       ['2013-01-07', 0, 0.999913452106, -0.700480071906, 0.911512370843],
			                       ['2013-01-08', 0, 0.712038046822, 0.353666429071, 0.190055423761],
			                       ['2014-01-13', 10, 0.987127460968, -1.77156121034, 1.01214030496],
			                       ['2014-01-13', 1, 0.881928349698, -2.19331177439, 1.77889434406],
			                       ['2014-02-25', 10, 0.0875528346389, 1.30569522004, 0.524964784217],
			                       ['2014-02-25', 1, 0.12658432064, 1.95385057303, 0.174847905936],
			                       ['2014-09-16', 100, 0.901128927601, -4.12735096256, 3.78735462682],
			                       ['2014-09-18', 100, 0.792842499024, -3.06172823977, 1.77689278967]
		                       ], columns=['Date', 'Gain', 'Rsquared', 'A_coeff', 'B_coeff'])

		try:
			cdt.load_regression_data(self.df)
		except IntegrityError:
			pass  # it's probably OK in this case - it should mean the data is already there - tests will fail later if it isn't

	def test_check_row_exists(self):

		session = classes.get_new_session()
		try:
			self.assertFalse(cdt.check_gain_reg_exists(session, '2013-01-09', 0))  # wrong date
			self.assertFalse(cdt.check_gain_reg_exists(session, '2013-01-08', 10))  # wrong gain
			self.assertTrue(cdt.check_gain_reg_exists(session, '2014-01-13', 10))  # right date + gain
		finally:
			session.close()

	def test_check_lookup(self):
		session = classes.get_new_session()

		try:
			regression = cdt.lookup_regression_values(session, '2013-01-08', 0)
			self.assertAlmostEqual(regression.r_squared, 0.712038046822)
			self.assertAlmostEqual(regression.a_coefficient, 0.35366642907099999)
			self.assertAlmostEqual(regression.b_coefficient, 0.19005542376099999)

			regression = cdt.lookup_regression_values(session, '2014-01-13', 1)
			self.assertAlmostEqual(regression.r_squared, 0.8819283496979999)
			self.assertAlmostEqual(regression.a_coefficient, -2.19331177439)
			self.assertAlmostEqual(regression.b_coefficient, 1.7788943440599998)
		finally:
			session.close()

	def test_chl_decision(self):

		# tests decision tree when there only exists gain 0 Chl values
		# gain 0 with a r-square value that is significant
		self.assertAlmostEqual(cdt.chl_decision(10, '2013-01-07'), 8.41464364)
		# gain 0 with a nonsignificant r-square value
		self.assertEqual(cdt.chl_decision(10, '2013-01-08'), 10)

		# when the uncorrected value is less than 5 use gain 100 regression
		# gain 100 sig
		self.assertAlmostEqual(cdt.chl_decision(4, '2014-09-16'), 11.02206754472)
		# gain 100 no sig
		self.assertEqual(cdt.chl_decision(4, '2014-09-18'), 4)

		# when the uncorrected value is less than 45 but greater than 5 use gain 10
		# gain 10 sig
		self.assertAlmostEqual(cdt.chl_decision(10, '2014-01-13'), 8.34984184)
		# gain 10 no sig
		self.assertEqual(cdt.chl_decision(10, '2014-02-25'), 10)

		# the rest of the time just use the gain 1 correction
		# gain 1 sig
		self.assertAlmostEqual(cdt.chl_decision(50, '2014-01-13'), 86.75140543, places=5)  # set places shorter - we think there's a typo in "43" - should be insignificant regardless
		# gain 1 no sig
		self.assertEqual(cdt.chl_decision(50, '2014-02-25'), 50)

	def test_chl_decision_no_regression(self):
		self.assertEqual(cdt.chl_decision(4, '1000-02-25'), 4)
		pass


if __name__ == '__main__':
	unittest.main()
