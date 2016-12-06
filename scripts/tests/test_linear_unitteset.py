import arcpy
import numpy as np
import unittest
from scripts import linear_ref

class MeasTableTests(unittest.TestCase):

	def setUp(self):
		self.recs = [[64, 'CA', 12060.5], [25, 'F1', 2060.5]]
		self.dts = {'names': ('ID', 'text', 'MEAS'),
		       'formats': (np.uint8, 'S1',  np.float32)}
		self.array = np.rec.fromrecords(self.recs, dtype=self.dts)
		pass

	def test_PairDict(self):
		arcpy.da.NumPyArrayToTable(self.array, "in_memory/out_table1")
		self.assertEqual(linear_ref.ID_MeasurePair("in_memory/out_table1", 'ID'), {64: 12060.5, 25: 2060.5})
		pass


class LinRefTests(unittest.TestCase):

	def setUp(self):
		self.recs = [[64, 'CA', -153363.923533, 33135.571809], [25, 'F1', -151940.398463, 32115.633976]]
		self.dts = {'names': ('ID', 'text', 'x_coord', 'y_coord',),
		       'formats': (np.uint8, 'S2',  np.float64, np.float64)}
		self.array = np.rec.fromrecords(self.recs, dtype=self.dts)
		pass

	def test_featurelayer(self):
		arcpy.da.NumPyArrayToTable(self.array, "in_memory/np_table")
		feature_layer = linear_ref.makeFeatureLayer("in_memory/np_table")
		desc = arcpy.Describe(feature_layer)

		# check output is a feature class
		self.assertEqual(desc.dataType, "FeatureClass")

		# test spatial reference
		self.assertEqual(desc.spatialReference.exportToString(),
		                 arcpy.SpatialReference(3310).exportToString()) # CA Teale Albers

		# make sure temp_layer is deleted
		self.assertFalse(arcpy.Exists("temp_layer"))
		pass

	def test_locate(self):
		arcpy.da.NumPyArrayToTable(self.array, "in_memory/np_table2")
		out_layer = linear_ref.makeFeatureLayer("in_memory/np_table2")
		ref_table_out = linear_ref.LocateWQalongREF(out_layer)
		cursor = arcpy.da.SearchCursor(ref_table_out, ['ID', 'text', 'Meas'])

		results = []
		for row in cursor:
			results.append(row)

		self.assertEqual(results[0], (64, u'CA', 5198.630391043295))  # why so many sig figs???
		self.assertEqual(results[1], (25, u'F1', 3321.5817420431454))

		pass

if __name__ == '__main__':
	unittest.main()
