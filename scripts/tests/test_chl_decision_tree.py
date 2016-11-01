import unittest
from scripts import chl_decision_tree

class ChlCorrection(unittest.TestCase):

	def setUp(self):
		self.a = 8.3
		self.b = 1.3
		self.raw = 6.1
		pass

	def test_data_headers(self):
		self.assertEqual(chl_decision_tree.chl_correction(self.raw, self.a, self.b), 16.23)
		pass


if __name__ == '__main__':
	unittest.main()
