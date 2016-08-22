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
	wq = pandas.read_csv(csv_from_miniSonde, header=9, parse_dates=[[0, 1]], na_values='#')

	# drop first row which contains units with illegal characters
	wq = wq.drop(wq.index[[0]])

	# drop all columns that are blank since data in csv is separated by empty columns
	wq = wq.dropna(axis=1, how="all")

	# change Date_Time to be ISO8603 (ie no slashes in date)
	wq['Date_Time'] = pandas.to_datetime(wq['Date_Time'], format='%m/%d/%Y %H:%M:%S')

	return wq


def shp2dataframe(fname):
	"""
	Makes a Pandas DataFrame from a shapefile.dbf with XY coords
	"""
	r = shapefile.Reader(fname)  # opens shapefile reader
	fields = r.fields

	# get list of fields names - fields in format of (GPS_Date, D, 8, 0)
	fieldnames = []
	for field in fields:
		fieldnames.append(field[0])

	# pop off "DeletionFlag"
	fieldnames.remove('DeletionFlag')
	# add XY
	fieldnames.append('XY')

	data = []
	for sr in r.shapeRecords():
		data.append(sr.record + sr.shape.points)
	df = pandas.DataFrame(data, columns=fieldnames)
	return df


def TimestampFromDateTime(date, time):
	"""
	:param: date in format of [2013, 4, 4], time '08:18:47am'
	:return: datetime object
	"""
	date = '{0} {1} {2} {3}'.format(date[0], date[1], date[2], time)
	date_object = datetime.strptime(date, '%Y %m %d %I:%M:%S%p')
	return date_object


def addCombinedDateTime(df, datefieldname, timefieldname):
	df['Date_Time'] = df.apply(lambda row: TimestampFromDateTime(row[datefieldname], row[timefieldname]), axis=1)
	return


def replaceIllegalFieldnames(df):
	df = df.rename(columns={'CHL.1': 'CHL_VOLTS', 'DO%': 'DO_PCT'}) # TODO make this catch other potential errors
	return df



def JoinByTimeStamp(wq_df, shp_df):
	"""
	Joins two pandas dataframes using the Date Time fields
	:param wq_df: water quality data frame - destination (inner join)
	:param shp_df: dataframe from the shapefile - ie xy coordinates
	:return: data frame with water quality data and gps corordinates
	"""
	# use left join to match gps data to water quality
	mergedDF = pandas.merge(wq_df, shp_df, how="left", left_on="Date_Time", right_on="Date_Time")

	# the rows that are matches!
	matchDF = mergedDF[mergedDF["XY"].notnull()]

	# the rows with missing data
	notmatchDF = mergedDF[mergedDF["XY"].isnull()]

	return matchDF, notmatchDF


def JoinMatchPercent(original, joined):
	percent_match = float(joined.shape[0]) / float(original.shape[0]) * 100
	return percent_match


def addsourcefield(dataframe, fieldName, source):
	base = os.path.basename(source)
	dataframe[fieldName] = base
	return


def transect_join_timestamp(waterquality_csv, transect_shapefile_points):

	# water quality
	wq = wq_from_csv(waterquality_csv)

	# replace illegal fieldnames
	wq = replaceIllegalFieldnames(wq)

	# add source for water quality file
	addsourcefield(wq, "WQ_SOURCE", waterquality_csv)

	# shapefile for transect
	pts = shp2dataframe(transect_shapefile_points)

	# add date_time field
	addCombinedDateTime(pts, "GPS_Date", "GPS_Time")

	# add GPS file source
	addsourcefield(pts, "GPS_source", transect_shapefile_points)

	# join using time stamps w/ exact match
	joined_data = JoinByTimeStamp(wq, pts)

	matches = joined_data[0]

	return matches





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
		w.point(xy[0], xy[1])

	# add fields for dbf
	for k, column in enumerate(df.columns):
		print(column)
		column = str(column)  # unicode strings freak out pyshp, so remove u'..'


		# TODO ugg messy way to convert types
		numberfields = ["Temp", "pH", "SpCond", "Sal", "DEP25", "PAR", "RPAR", "TurbSC", "CHL", "CHL_VOLTS"]

		for field in numberfields:
			df[field] = df[field].astype(np.float)

		# print out the column type
		#print(df.dtypes[k])

		if np.issubdtype(df.dtypes[k], np.number): #TODO this dosn't work correctly becuase it's a py obj
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


def df2database(data):
	# appends data to SQL database
	# THIS is JUST PSEUDOCODE right now
	data.to_sql(table_name, connection, flavor='sqlite', if_exists='append')
	return


def main(water_quality_csv, GPS_points, output_shapefile):
	"""
	:param water_quality_csv:
	:param GPS_points:
	:param output_shapefile:
	:return: shapefile with water quality data matched by time stamps
	"""

	# process water quality
	matches = transect_join_timestamp(water_quality_csv, GPS_points)

	# water quality as dataframe to report percent matched
	wq_df = wq_from_csv(water_quality_csv)

	print("Percent Matched: {}".format(JoinMatchPercent(wq_df, matches)))

	print("Saving matches to shapefile")
	# save matches to shapefile
	write_shp(output_shapefile, matches)

	# copy projection from source
	copyPRJ(GPS_points, output_shapefile)


