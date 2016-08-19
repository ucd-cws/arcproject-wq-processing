# match shp and water quality data by timestamp
import pandas
import shapefile
import os
import numpy as np
from datetime import datetime
from shutil import copyfile

# load a water quality file
def wq_from_csv(csv_from_miniSonde):
	"""
	:param csv_from_miniSonde: raw data file containing water quality data
	:return: water quality as pandas dataframe
	"""

	# load data from the csv starting at row 11, combine Date/Time columns using parse dates
	wq = pandas.read_csv(csv_from_miniSonde, header=9, parse_dates=[[0, 1]])

	# drop first row which contains units with illegal characters
	wq = wq.drop(wq.index[[0]])

	# drop all columns that are blank since data in csv is separated by empty columns
	wq = wq.dropna(axis=1, how="all")

	# change Date_Time to be ISO8603 (ie no slashes in date)
	wq['Date_Time'] = pandas.to_datetime(wq['Date_Time'], format='%m/%d/%Y %I:%M:%S')

	return wq


def dateFromRecord(record):
	"""
	:param record: date in format of [[2013, 4, 4], '08:18:47am']
	:return: datetime object
	"""
	date = '{0} {1} {2} {3}'.format(record[0][0], record[0][1], record[0][2], record[1])
	date_object = datetime.strptime(date, '%Y %m %d %I:%M:%S%p')
	return date_object


# geopandas is a pain to install on windows so let's try to use pyshp to turn dbf into dataframe

def shp2dataframe(fname):
	"""
	Makes a Pandas DataFrame from a shapefile.dbf with XY coords
	"""
	r = shapefile.Reader(fname)  # opens shapefile reader
	data = []
	for sr in r.shapeRecords():
		dt = dateFromRecord(sr.record)
		data.append([dt] + sr.shape.points)
	df = pandas.DataFrame(data, columns=["Date", "XY"])
	return df


def JoinByTimeStamp(wq_df, shp_df):
	"""
	Joins two pandas dataframes using the Date Time fields
	:param wq_df: water quality data frame - destination (inner join)
	:param shp_df: dataframe from the shapefile - ie xy coordinates
	:return: data frame with water quality data and gps corordinates
	"""
	# use left join to match gps data to water quality
	mergedDF = pandas.merge(wq_df, shp_df, how="left", left_on="Date_Time", right_on="Date")

	# the rows that are matches!
	matchDF = mergedDF[mergedDF["XY"].notnull()]

	# the rows with missing data
	notmatchDF = mergedDF[mergedDF["XY"].isnull()]

	return matchDF, notmatchDF


def nrows(df):
	# number of rows in a pandas data frame
	n = df.shape[0]
	return n


def JoinMatchPercent(original, joined):
	percent_match = float(nrows(joined)) / float(nrows(original)) * 100
	return percent_match


def JoinDiff(original, joined):
	diff = nrows(original) - nrows(joined)
	return diff


def replaceIllegalFieldnames(df):
	df = df.rename(columns={'CHL.1': 'CHL_VOLTS', 'DO%': 'DO_PCT'}) # TODO make this catch other potential errors

	return df


def write_shp(filename, dataframe, write_index=True):
	"""Write dataframe w/ geometry to shapefile.

	from https://github.com/ojdo/python-tools/blob/master/pandashp.py

	Args:
		filename: ESRI shapefile name to be written (without .shp extension)
		dataframe: a pandas DataFrame with column geometry and homogenous
				   shape types (Point, LineString, or Polygon)
		write_index: add index as column to attribute tabel (default: true)

	Returns:
		Nothing.
	"""

	df = dataframe.copy()

	geometry = df.pop('XY')

	w = shapefile.Writer(shapefile.POINT)
	for xy in geometry:
		print(xy)
		w.point(xy[0], xy[1])

	# add fields for dbf
	for k, column in enumerate(df.columns):
		column = str(column)  # unicode strings freak out pyshp, so remove u'..'
		print(column)
		print(df.dtypes[k])
		if np.issubdtype(df.dtypes[k], np.number): #TODO this dosn't work correctly becuase it's a py obj
			# detect and convert integer-only columns
			if (df[column] % 1 == 0).all():
				df[column] = df[column].astype(np.integer)

			# now create the appropriate fieldtype
			if np.issubdtype(df.dtypes[k], np.floating):
				w.field(column, 'N', decimal=5)
			else:
				w.field(column, 'I', decimal=0)
		elif np.issubdtype(df.dtypes[k], np.object): # quick work around to force all columns in shp to be float
			w.field(column, 'N', decimal=5)
		else:
			w.field(column)

	# add records to dbf
	for record in df.itertuples():
		w.record(*record[1:])  # drop first tuple element (=index)

	w.save(filename)


def copyPRJ(in_shp, out_shp):
	# copies source .prj to output .prj
	# TODO might be a much better way to do this with pyproj
	in_base = os.path.splitext(in_shp)[0]
	src = in_base + '.prj'
	out_base = os.path.splitext(out_shp)[0]
	dst = out_base + '.prj'
	copyfile(src, dst)


def main(water_quality_csv, GPS_points, output_shapefile):
	"""
	:param water_quality_csv:
	:param GPS_points:
	:param output_shapefile:
	:return: shapefile with water quality data matched by time stamps
	"""

	# process water quality
	print("Processing Water Quality")
	wq_df = wq_from_csv(water_quality_csv)

	print("Processing GPS data")
	# process gps data
	shp_d = shp2dataframe(GPS_points)

	print("Matching....")
	# join by timestamp
	matches = JoinByTimeStamp(wq_df, shp_d)[0]
	matches = replaceIllegalFieldnames(matches)

	print("Percent Matched: {}".format(JoinMatchPercent(wq_df, matches)))

	print("Saving matches to shapefile")
	# save matches to shapefile
	write_shp(output_shapefile, matches)

	# copy projection from source
	copyPRJ(GPS_points, output_shapefile)



