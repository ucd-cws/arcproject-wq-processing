# -*- coding: utf-8 -*-

import os
import unittest
from datetime import datetime
import six

import pandas
import arcpy

from scripts import wqt_timestamp_match
from waterquality import classes
from sqlalchemy import exc

class BaseDBTest(unittest.TestCase):
	"""
		This class is used as the base for a number of other database tests but doesn't have tests of its own
	"""

	def setUp(self):
		self.wq = os.path.join("testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqt_cc.csv")
		self.gps = os.path.join("testfiles", "Arc_040413", "Arc_040413_GPS", "040413_PosnPnt.shp")
		self.site_code = "WQT"
		self.session = classes.get_new_session()
		self._make_site()

		self.pre_test_num_records = self.session.query(classes.WaterQuality.id).filter(classes.Site.code == self.site_code).count()

	def _make_site(self):
		"""
			When testing on test server, database will be cleaned first, but when DB exists, we'll need to check if the site
			exists, and only create it when it doesn't exist
		:return:
		"""

		if self.session.query(classes.Site).filter(classes.Site.code == self.site_code).one_or_none() is None:
			new_site = classes.Site()
			new_site.code = self.site_code
			new_site.name = "Testing Site"
			self.session.add(new_site)
			self.session.commit()


class TestUnitConversion(unittest.TestCase):

	def setUp(self):
		self.wq = os.path.join("testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqt_cc.csv")
		self.df = wqt_timestamp_match.wq_from_file(self.wq)  # doesn't really matter that units are already converted here - the test is just going to pretend anyway
		self.unmodified_data = self.df["DEP25"]
		self.unmodified_other_column = self.df["pH"]

		self.units = {
			u"DEP25": u"feet",
			u"Temp": u"°C",
			u"SpCond": u"µS/cm",
			u"DO%": u"Sat",
			u"DO_PCT": u"Sat",
			u"DO": u"mg/l",
			u"PAR": u"µE/s/m²",
			u"RPAR": u"µE/s/m²",
			u"TurbSC": u"NTU",
			u"CHL": u"µg/l",
			u"CHL_VOLTS": u"Volts",
			u"Sal": None,
			u"pH": None,
			u"Date": None,
			u"Time": None,
			u"Date_Time": None,
			u"WQ_SOURCE": None,
			u"GPS_SOURCE": None,
			u"GPS_Time": None,
			u"GPS_Date": None,
			u"POINT_Y": None,
			u"POINT_X": None,
		}

	def test_convert_type(self):

		converted_df = wqt_timestamp_match.check_and_convert_units(self.df, self.units)

		#if sys.maxsize > 2**32:  # basically, if we're running in 64 bit Python (checks if the largest number is larger than the max number a 32 bit integer can hold
		#	dtype = "float64"
		#else:
		#	dtype = "float32"

		self.assertEqual(converted_df["DEP25"].dtype, "float64")  # check the data type since it would have had to be converted to change the units
		for index, value in enumerate(self.unmodified_data):  # make sure that
			self.assertEqual(float(value) * 0.3048, converted_df["DEP25"][index+1])  # records aren't 0 indexed - multiplies the one value * 0.3048 to confirm the other transformation was correct - doesn't test other cases yet, but we don't have any

		for index, value in enumerate(self.unmodified_other_column):
			self.assertEqual(value, self.df["pH"][index+1])  # make sure that other columns weren't changed

	def test_fail_on_unknown_units(self):

		temp_real_units = self.units["Temp"]
		self.units["Temp"] = None  # set it to a bad value now

		with self.assertRaises(KeyError):
			wqt_timestamp_match.check_and_convert_units(self.df, self.units)  # make sure it fails when bad units are put in

		self.units["Temp"] = temp_real_units  # restore it for future tests in the same session


class TestDFLoading(unittest.TestCase):
	def setUp(self):
		"""
			Set the path to normal data and foot data
		:return:
		"""
		self.wq_meters = os.path.join("testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqt_cc.csv")
		self.wq_feet = os.path.join("testfiles", "feet_conversion.csv")

	def load_file(self, filepath):
		"""
			Imitates the first part of the data loading code in wqt_timestamp_match
		:param filepath:
		:return:
		"""

		if six.PY3:  # pandas chokes loading the documents if they aren't encoded as UTF-8 on Python 3. This creates a copy of the file that's converted to UTF-8.
			water_quality_raw_data = wqt_timestamp_match.convert_file_encoding(filepath)
			encoding = "utf-8"
		else:
			encoding = "latin_1"  # absolutely necessary. Without this, Python 2 assumes it's in ASCII and then our units line (like the degree symbol) is gibberish and can't be compared
			water_quality_raw_data = filepath

		wq = pandas.read_csv(water_quality_raw_data, header=9, parse_dates=[[0, 1]], na_values='#',
			                 encoding=encoding)  # TODO add other error values (2000000.00 might be error for CHL)

		# drop all columns that are blank since data in csv is separated by empty columns
		wq = wq.dropna(axis=1, how="all")
		return wqt_timestamp_match.replaceIllegalFieldnames(wq)

	def test_no_data_conversion(self):
		df = wqt_timestamp_match.wq_from_file(self.wq_meters)
		wq = self.load_file(self.wq_meters)

		for index, value in enumerate(wq["DEP25"]):
			if index == 0:
				print("skipping header")
			else:
				# print(value, df["DEP25"][index])
				self.assertEqual(value, df["DEP25"][index])

	def test_data_conversion(self):
		df = wqt_timestamp_match.wq_from_file(self.wq_feet)
		wq = self.load_file(self.wq_feet)

		for index, value in enumerate(wq["DEP25"]):
			if index == 0:
				print("skipping header")
			else:
				self.assertEqual(float(value) * 0.3048, df["DEP25"][index])


class TestDBInsert(BaseDBTest):

	def test_data_insert(self):
		matched = wqt_timestamp_match.wq_from_file(self.wq)
		wqt_timestamp_match.wq_df2database(matched, session=self.session)

		expected = len(matched)
		added = len(self.session.new)
		try:
			self.session.commit()
		except exc.IntegrityError as e:
			print(e)
			print("Water quality data already exists in database.")

		self.session.close()
		self.assertEqual(expected, added)  # assert at end so that database commit occurs and we can inspect

	# This test fails since the data does not get added to the database if it already exists since
	# test_data_insert catches the IntegrityError

	def test_records_in_db(self):
		self.test_data_insert()
		num_records = self.session.query(classes.WaterQuality.id).filter(classes.Site.code == self.site_code).count()
		self.assertEqual(977, num_records)


class LoadWQ(unittest.TestCase):

	def setUp(self):
		self.data = os.path.join("testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqt_cc.csv")

	def test_data_headers(self):
		headers = wqt_timestamp_match.wq_from_file(self.data).columns.values

		for head in headers:
			self.assertIn(head, ['Date_Time', 'Temp', 'pH', 'SpCond', 'DO%', 'DO', 'DEP25',
			                     'PAR', 'RPAR', 'TurbSC', 'CHL', 'CHL_VOLTS', 'Sal', 'WQ_SOURCE'])

	def test_data_length(self):
		self.assertEqual(wqt_timestamp_match.wq_from_file(self.data).shape, (977, 12))


class LoadSHP(unittest.TestCase):
	"""
		Requires ArcGIS 10.4 or Pro 1.3 or above because we need datetimes in numpy arrays
	"""

	def setUp(self):
		self.data = os.path.join("testfiles", "Arc_040413", "Arc_040413_GPS", "040413_PosnPnt.shp")
		self.shpdf = wqt_timestamp_match.wqtshp2pd(self.data)

	def test_length(self):
		self.assertEqual(self.shpdf.shape, (15976, 6))

	def test_headers(self):
		headers = self.shpdf.columns.values
		for head in headers:
			self.assertIn(head, ['Date_Time', 'GPS_SOURCE', 'GPS_Date', 'GPS_Time', 'POINT_X', 'POINT_Y'])

	def test_coordinate_system(self):
		"""
			Ensures that the reprojection code properly returns a new dataset that matches the default coordinate system.
		:return:
		"""
		projected_data = wqt_timestamp_match.reproject_features(self.data)

		desc = arcpy.Describe(projected_data)
		self.assertEqual(desc.spatialReference.factoryCode, wqt_timestamp_match.projection_spatial_reference)


class CheckDates(unittest.TestCase):

	def setUp(self):
		self.date = '2013-4-4'
		self.time = '08:18:47am'
		self.date_time = wqt_timestamp_match.TimestampFromDateTime(self.date, self.time)
		pass

	def test_ISO8601(self):
		self.assertEqual(self.date_time.strftime("%Y-%m-%dT%H:%M:%S"), self.date_time.isoformat())

	def test_DST(self):
		# make example date time into a dataframe with "Date_Time"
		self.df = pandas.DataFrame({'Date_Time': [self.date_time]})

		# add/subtract an hour
		self.plus1 = wqt_timestamp_match.dstadjustment(self.df, 1)
		self.minus1 = wqt_timestamp_match.dstadjustment(self.df, -1)

		# get first row
		self.plus1hr = self.plus1.loc[0]['Date_Time']
		self.minus1hr = self.minus1.loc[0]['Date_Time']

		# test against string
		self.assertEqual(self.plus1hr, datetime.strptime('2013-04-04 09:18:47', '%Y-%m-%d %H:%M:%S'))
		self.assertEqual(self.minus1hr, datetime.strptime('2013-04-04 07:18:47', '%Y-%m-%d %H:%M:%S'))


class CheckJoin(BaseDBTest):

	def setUp(self):

		super(CheckJoin, self).setUp()

		wq = wqt_timestamp_match.wq_append_fromlist([self.wq])

		# shapefile for transect
		pts = wqt_timestamp_match.wqtshp2pd(self.gps)

		# join using time stamps with exact match
		self.joined_data = wqt_timestamp_match.JoinByTimeStamp(wq, pts)
		self.matches = wqt_timestamp_match.splitunmatched(self.joined_data)[0]

		wqt_timestamp_match.wq_df2database(self.matches, session=self.session)


	def test_data_insert(self):

		expected = len(self.matches)
		added = len(self.session.new)

		self.assertEqual(expected, added)  # assert at end so that database commit occurs and we can inspect

	def check_latitude_and_longitude(self):

		for record in self.session.new:
			self.assertIsNotNone(record.x_coord)
			self.assertIsNotNone(record.y_coord)

	def tearDown(self):
		#self.session.commit()
		self.session.close()

class CheckReprojection(BaseDBTest):

	def setUp(self):
		super(CheckReprojection, self).setUp()

		self.wq = wqt_timestamp_match.wq_append_fromlist([self.wq])

		# shapefile for transect
		self.pts = wqt_timestamp_match.wqtshp2pd(self.gps)

		# join using time stamps with exact match
		self.joined_data = wqt_timestamp_match.JoinByTimeStamp(self.wq, self.pts)
		self.matches = wqt_timestamp_match.splitunmatched(self.joined_data)[0]
		wqt_timestamp_match.wq_df2database(self.matches, session=self.session)


	def test_spatial_reference_code_in_db(self):

		wq_objects = self.session.new
		for wqo in wq_objects:
			self.assertEqual(wqo.spatial_reference_code, wqt_timestamp_match.projection_spatial_reference)

	def test_coordinates_in_bounds(self):
		"""
			This comes close to testing functionality in another library, but we check if the coordinates attached to
			each record are in bounds for the spatial reference as another way of ensuring that the transformation occurred
			and that the attributes were all properly set both for the spatial reference and the coordinates.

			This test currently isn't very useful because most coordinates (including Decimal Degrees) are
			within the domain returned for California Teale Albers. Everything should be true here.
		:return:
		"""

		coordinate_system = arcpy.SpatialReference(wqt_timestamp_match.projection_spatial_reference)

		x_min, y_min, x_max, y_max = coordinate_system.domain.split(" ")

		for record in self.session.new:
			self.assertTrue(float(x_min) <= float(record.x_coord) <= float(x_max))
			self.assertTrue(float(y_min) <= float(record.y_coord) <= float(y_max))




if __name__ == '__main__':
	unittest.main()
