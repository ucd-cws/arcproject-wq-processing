import unittest
import pandas as pd
import os

from sqlalchemy.exc import IntegrityError
from datetime import datetime
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

		# this is a list of regression objects
		self.regs = [
			classes.Regression(id=1, date=datetime(2013, 1, 7).date(), gain=0, r_squared=0.999913452106, a_coefficient= -0.700480071906, b_coefficient=0.911512370843),
			classes.Regression(id=2, date=datetime(2013, 1, 8).date(), gain=0, r_squared=0.712038046822, a_coefficient= 0.353666429071, b_coefficient=0.190055423761),
			classes.Regression(id=3, date=datetime(2014, 1, 13).date(), gain=10, r_squared=0.987127460968, a_coefficient= -1.77156121034, b_coefficient=1.01214030496),
			classes.Regression(id=4, date=datetime(2014, 1, 13).date(), gain=1, r_squared=0.881928349698, a_coefficient= -2.19331177439, b_coefficient=1.77889434406),
			classes.Regression(id=5, date=datetime(2014, 2, 25).date(), gain=10, r_squared=0.0875528346389, a_coefficient= 1.30569522004, b_coefficient=0.524964784217),
			classes.Regression(id=6, date=datetime(2014, 2, 25).date(), gain=1, r_squared=0.12658432064, a_coefficient=1.95385057303, b_coefficient=0.174847905936),
			classes.Regression(id=7, date=datetime(2014, 9, 16).date(), gain=100, r_squared=0.901128927601, a_coefficient= -4.12735096256, b_coefficient=3.78735462682),
			classes.Regression(id=8, date=datetime(2014, 9, 18).date(), gain=100, r_squared=0.792842499024, a_coefficient= -3.06172823977, b_coefficient=1.77689278967),
			classes.Regression(id=9, date=datetime(2014, 9, 18).date(), gain=100, r_squared=0.792842499024, a_coefficient= -3.06172823977, b_coefficient=1.77689278967)
		]
		pass

	def test_structure(self):
		# regs is a list
		self.assertEqual(type(self.regs), list)

		# items in regs are of type classes.Regression
		self.assertEqual(type(self.regs[0]), classes.Regression)

		# check the value of variable in a class instance
		self.assertEqual(self.regs[0].r_squared, 0.999913452106)

	def test_check_gainrow_exists(self):
		self.assertFalse(cdt.check_gain_reg_exists(self.regs, datetime(2013, 1, 9), 0))  # wrong date
		self.assertFalse(cdt.check_gain_reg_exists(self.regs, datetime(2013, 1, 8), 10))  # wrong gain
		self.assertTrue(cdt.check_gain_reg_exists(self.regs, datetime(2014, 1, 13), 10))  # right date + gain

	def test_RegComp(self):
		self.assertEqual(cdt.RegListComp(self.regs, datetime(2014, 1, 13), 10), self.regs[2])
		self.assertEqual(cdt.RegListComp(self.regs, datetime(2014, 9, 16), 100), self.regs[6])

	def test_RegComp_nodata_exception(self):
		with self.assertRaises(Exception) as context:
			cdt.RegListComp(self.regs, datetime(2014, 9, 18), 0)
		self.assertTrue('Regression values does not exist for this date and gain setting!' in str(context.exception))

	def test_RegComp_duplicate_exception(self):
		with self.assertRaises(Exception) as context:
			cdt.RegListComp(self.regs, datetime(2014, 9, 18), 100)
		self.assertTrue("Regression values for date and gain must be unique!" in str(context.exception))

	def test_get_chl_for_gain(self):
		# gain 0 with a r-square value that is significant
		self.assertAlmostEquals(cdt.get_chl_for_gain(10, self.regs, datetime(2013, 1, 7), 0), 8.41464364, places=5)

		# gain 0 with a nonsignificant r-square value
		self.assertAlmostEquals(cdt.get_chl_for_gain(10, self.regs, datetime(2013, 1, 8), 0), 10, places=5)

	def test_cdt(self):
		# gain 0 with a nonsignificant r-square value
		self.assertEqual(cdt.chl_decision(10, self.regs, datetime(2013, 1, 8)), 10)

		# when the uncorrected value is less than 5 use the gain 100 regression
		# gain 100 sig
		self.assertAlmostEqual(cdt.chl_decision(4, self.regs, datetime(2014, 9, 16)), 11.02206754472, places=5)

		#when the uncorrected value is less than 45 but greater than 5 use gain 10
		# gain 10 sig
		self.assertAlmostEqual(cdt.chl_decision(10, self.regs, datetime(2014, 1, 13)), 8.34984184, places=5)
		# gain 10 no sig
		self.assertEqual(cdt.chl_decision(10, self.regs, datetime(2014, 2, 25)), 10)

		# the rest of the time just use the gain 1 correction
		# gain 1 sig
		self.assertAlmostEqual(cdt.chl_decision(50, self.regs, datetime(2014, 1, 13)), 86.75140543, places=5)
		# gain 1 no sig
		self.assertEqual(cdt.chl_decision(50, self.regs, datetime(2014, 2, 25)), 50)

	def test_chl_decision_no_regression(self):
		self.assertEqual(cdt.chl_decision(4, self.regs, datetime(1000, 2, 25)), None)
		pass


if __name__ == '__main__':
	unittest.main()
