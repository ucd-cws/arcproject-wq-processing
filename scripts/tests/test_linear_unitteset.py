import os
import arcpy
import numpy as np
import unittest
from scripts import linear_ref

class TableTests(unittest.TestCase):

	def setUp(self):
		self.recs = [[64, 'CA', 12060.5], [25, 'F1', 2060.5]]
		self.dts = {'names': ('ID', 'text', 'MEAS'),
		       'formats': (np.uint8, 'S1',  np.float32)}
		self.array = np.rec.fromrecords(self.recs, dtype=self.dts)
		pass

	def test_PairDict(self):
		arcpy.da.NumPyArrayToTable(self.array, r"in_memory/out_table")
		self.assertEqual(linear_ref.ID_MeasurePair(r"in_memory/out_table", 'ID'), {64: 12060.5, 25: 2060.5})
		pass


if __name__ == '__main__':
	unittest.main()