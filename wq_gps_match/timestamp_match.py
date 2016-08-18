# match shp and water quality data by timestamp
import pandas

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


# load a shapefile using the geopandas

