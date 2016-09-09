# match shp and water quality data by timestamp
import pandas as pd
import os
from datetime import datetime, timedelta
import geopandas as gpd


# load a water quality file
def wq_from_csv(csv_from_sonde):
	"""
	:param csv_from_Sonde: raw data file containing water quality data
	:return: water quality as pandas dataframe
	"""

	# load data from the csv starting at row 11, combine Date/Time columns using parse dates
	wq = pd.read_csv(csv_from_sonde, header=9, parse_dates=[[0, 1]], na_values='#') # TODO add other error values (2000000.00 might be error for CHL)

	# drop first row which contains units with illegal characters
	wq = wq.drop(wq.index[[0]])

	# drop all columns that are blank since data in csv is separated by empty columns
	wq = wq.dropna(axis=1, how="all")

	# replace illegal fieldnames
	wq = replaceIllegalFieldnames(wq)

	# add column with source
	addsourcefield(wq, "WQ_SOURCE", csv_from_sonde)

	# change Date_Time to be ISO8603 (ie no slashes in date)
	try:
		wq['Date_Time'] = pd.to_datetime(wq['Date_Time']) #, format='%m/%d/%Y %H:%M:%S')

	except ValueError:
		print("Time is in a format that is not supported. Try using '%m/%d/%Y %H:%M:%S' .")

	return wq


def TimestampFromDateTime(date, time):
	"""
	:param: date in format of [2013, 4, 4], time '08:18:47am'
	:return: datetime object
	"""
	dt = date + 't' + time
	date_object = datetime.strptime(dt, '%Y-%m-%dt%I:%M:%S%p')
	return date_object


def shp2gpd(shapefile):
	df = gpd.read_file(shapefile)
	addsourcefield(df, "GPS_SOURCE", shapefile)

	# combine GPS date and GPS time fields into a single column
	df['Date_Time'] = df.apply(lambda row: TimestampFromDateTime(row["GPS_Date"], row["GPS_Time"]), axis=1)

	# drop duplicated rows in the data frame
	df = df.drop_duplicates(["Date_Time"], keep='first')
	return df


def replaceIllegalFieldnames(df):
	df = df.rename(columns={'CHL.1': 'CHL_VOLTS', 'DO%': 'DO_PCT'}) # TODO make this catch other potential errors
	return df


def dstadjustment(df, offset_hours):
	df2 = df.copy()  # make a copy of data so original is not overwritten
	dstshift = lambda x: x + timedelta(hours=offset_hours)
	df2['Date_Time'] = df2['Date_Time'].map(dstshift)
	return df2


def addsourcefield(dataframe, fieldName, source):
	base = os.path.basename(source)
	dataframe[fieldName] = base
	return


def JoinByTimeStamp(wq_df, shp_df):
	"""
	Joins geopandas dataframe with the water quality attributes using the Date Time fields
	:param wq_df: water quality data frame
	:param shp_df: geo dataframe from the shapefile
	:return: geopandas dataframe with water quality data and gps coordinates
	"""
	# geopandas dataframe should be on left for the join in order for the output to be a gpd
	#mergedDF = pandas.merge(wq_df, shp_df, how="left", left_on="Date_Time", right_on="Date_Time")
	joined = shp_df.merge(wq_df, how="outer", on="Date_Time")
	return joined


def splitunmatched(joined_data):
	# returns all joined data that has a match (ie inner join),
	# the unmatched transect points (outer left) and unmatched water quality (outer right) points as separate dataframes

	match = joined_data.dropna(axis='index')
	no_geo = joined_data[joined_data["GPS_SOURCE"].isnull()]
	no_wq = joined_data[joined_data["WQ_SOURCE"].isnull()]

	return match, no_geo, no_wq


def JoinMatchPercent(original, joined):
	percent_match = float(joined.shape[0]) / float(original.shape[0]) * 100
	return percent_match


def wq_append_fromlist(list_of_csv_files):
	master_wq_df = pd.DataFrame()
	for csv in list_of_csv_files:
		try:
			pwq = wq_from_csv(csv)
			# append to master wq
			master_wq_df = master_wq_df.append(pwq)

		except:
			print("Unable to process: {}".format(csv))

	return master_wq_df


def gps_append_fromlist(list_gps_files):
	master_pts = pd.DataFrame()
	for gps in list_gps_files:
		try:
			# shapefile for transect
			pts = shp2gpd(gps)

			# append to master wq
			master_pts = master_pts.append(pts)

		except:
			print("Unable to process: {}".format(gps))

	return master_pts


def df2database(data):
	# appends data to SQL database
	# THIS is JUST PSEUDOCODE right now
	data.to_sql(table_name, connection, flavor='sqlite', if_exists='append')
	return


def geodf2shp(geodf, output_filename):
	# change timestamp values to strings
	geodf['Date_Time'] = geodf['Date_Time'].astype(str)

	# TODO ugg messy way to convert types
	numberfields = ["Temp", "pH", "SpCond", "Sal", "DEP25", "PAR", "RPAR", "TurbSC", "CHL"] # Why is DO missing?

	for field in numberfields:
		geodf[field] = geodf[field].astype(float)

	#print(geodf.dtypes)

	geodf.to_file(output_filename, driver="ESRI Shapefile")
	return


def main(water_quality_csv, GPS_points, output_shapefile):
	"""
	:param water_quality_csv:
	:param GPS_points:
	:param output_shapefile:
	:return: shapefile with water quality data matched by time stamps
	"""

	# water quality
	wq = wq_from_csv(water_quality_csv)

	# shapefile for transect
	pts = shp2gpd(GPS_points)

	# join using time stamps w/ exact match
	joined_data = JoinByTimeStamp(wq, pts)
	matches = splitunmatched(joined_data)[0]

	print("Percent Matched: {}".format(JoinMatchPercent(wq, matches)))

	geodf2shp(matches, output_shapefile)

	return

