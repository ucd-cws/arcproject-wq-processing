# match shp and water quality data by timestamp
import pandas
import shapefile
import os
import numpy as np
from datetime import datetime


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

	return wq


# load a shapefile using the pyshp


ex = os.path.join("examples", "Arc_040413_GPS", "040413_PosnPnt.shp")




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


test = shp2dataframe(ex)
print(test)