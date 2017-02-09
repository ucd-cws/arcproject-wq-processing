# linear reference points along sloughs
# given x, y and a reference line return distance along slough
import arcpy
from waterquality import classes
import mapping
import config
import datetime

def LocateWQalongREF(wq_features, ref_route):
	"""
	Uses arcpy linear refereeing to locate the input features distances along the reference route
	:param wq_features: water quality transect points as feature class
	:return: table with measurement along line, distance to ref line, etc.
	"""
	#  use linear referencing to locate each point along route using arcgis's linear referencing tool set
	if arcpy.Exists(r"in_memory\out_table"):
		# check if already exists and if so delete it
		arcpy.Delete_management(r"in_memory\out_table")
	ref_table_out = arcpy.LocateFeaturesAlongRoutes_lr(wq_features, ref_route, "SITECODE",
                                   "25 Meters", r"in_memory\out_table", out_event_properties="RID POINT MEAS")

	return ref_table_out


def MeasureDicts(linear_referenced_table, ID_field, update_sites=None):
	"""
	Creates a list of  python dicts with the each record ID and linear measurement along reference line
	:param linear_referenced_table: Table with linear reference results
	:param ID_field: Field name that uniquely identifies the record
	:param update_sites: when provided with a list of site objects, updates the site_id using ref value
	:return: list of dictionaries with id and m_value mappings
	"""
	cursor = arcpy.da.SearchCursor(linear_referenced_table, [ID_field, 'MEAS', 'RID'])
	dicts = []
	for row in cursor:
		if update_sites is None:
			measurePair = {'id': row[0], 'm_value': row[1]}
			dicts.append(measurePair)
		else:
			siteid = LookupSiteID(update_sites, row[2])
			measurePair = {'id': row[0], 'm_value': row[1], 'site_id': siteid}
			dicts.append(measurePair)
	return dicts


def pullSites(session):
	"""
	Creates query to pull records from the sites table
	:param session: an open SQLAlchemy database session
	:return: a list of site objects
	"""
	# pull all the data from the regression table in a single query
	# this avoids calling this for every records which spawns thousands of queries in the loop
	s = classes.Site
	s_table = session.query(s).all()
	return s_table


def LookupSiteID(sites_table, code):
	"""
	Filters the site table objects by code
	:param sites_table: a list objects of type site class
	:param code: code of site id to lookup
	:return: site id
	"""
	subset = [x for x in sites_table if (x.code == code)]
	if len(subset) == 1:
		siteid = subset[0].id
	elif len(subset) == 0:
		raise Exception("This site does not exist")
	return siteid


def getMvalues(query, sites_table=None):
	"""
	Given a SQLAlchemy query for water quality data, exports a feature class to linear reference which is used to update m_values
	:param query: a SQLAlchemy query object for records to update
	:param sites_table: a list of sites objects
	:return: data dict with id and m-value for records in query
	"""
	try:
		# turn records that need measurement to a feature class in memory
		if arcpy.Exists(r"in_memory\q_as_layer"):
			# check if already exists and if so delete it
			arcpy.Delete_management(r"in_memory\q_as_layer")
		mapping.query_to_features(query, "in_memory\q_as_layer")

		# locate features along route using the reference lines
		print("Locating points along routes....")
		meas_table = LocateWQalongREF("in_memory\q_as_layer", config.ref_line)

		# create data dict with ID and measurement result
		#distances = ID_MeasurePair(meas_table, "id")
		distances = MeasureDicts(meas_table, "id", sites_table)

	finally:
		# clean up temp layer
		arcpy.Delete_management(r"in_memory\q_as_layer")

	return distances


def bulk_updateM(session, idDistance_mappings):
	"""
	http://stackoverflow.com/questions/25694234/bulk-update-in-sqlalchemy-core-using-where
	:param session: an open SQLAlchemy database session
	:param idDistance: list of id~distance dict mappings
	:return:
	"""
	wq = classes.WaterQuality
	session.bulk_update_mappings(wq, idDistance_mappings)
	return


def queryBuilder(session, query_type="ALL", overwrite=False, idrange=None, dates=None):
	"""
	Creates query to pull records from water quality table
	:param session: an open SQLAlchemy database session
	:param query_type: choose "ALL", "IDRANGE", or "DATERANGE"
	:param overwrite: optional - overwrites any existing m values
	:param idrange: when query_type="IDRANGE" range of ids as list where [start_id, end_id]
		Ex: main("RANGE", overwrite=True, idrange=[120, 2000])
	:param dates: when query_type="DATERANGE" two datetime objects as list where [start_date, end_date].
		Ex: main("DATERANGE", overwrite=False, dates=[datetime.datetime(2016, 1, 01), datetime.datetime(2016, 1, 31)])
	:return: a SQLAlchemy query object
	"""
	wq = classes.WaterQuality

	if query_type == "ALL" and overwrite is True:
		# update all records in wq table that have xy coords
		q = session.query(wq).filter( wq.x_coord != None, wq.y_coord != None)
	elif query_type == "ALL" and overwrite is False:
		# update all records in wq table that have xy coords that don't have m - values
		q = session.query(wq).filter(wq.x_coord != None, wq.y_coord != None, wq.m_value == None)
	elif query_type == "IDRANGE" and overwrite is True and idrange is not None:
		q = session.query(wq).filter(wq.id >= idrange[0], wq.id <= idrange[1], wq.x_coord != None, wq.y_coord != None)
	elif query_type == "IDRANGE" and overwrite is False and idrange is not None:
		q = session.query(wq).filter(wq.id >= idrange[0], wq.id <= idrange[1], wq.x_coord != None,
		                             wq.y_coord != None, wq.m_value == None)
	elif query_type == "DATERANGE" and overwrite is True and dates is not None:
		upper_bound = dates[1] + datetime.timedelta(days=1)
		q = session.query(wq).filter(wq.date_time > dates[0], wq.date_time < upper_bound,
		                             wq.x_coord != None, wq.y_coord != None)
	elif query_type == "DATERANGE" and overwrite is False and dates is not None:
		upper_bound = dates[1] + datetime.timedelta(days=1)
		q = session.query(wq).filter(wq.date_time > dates[0], wq.date_time < upper_bound,
		                             wq.x_coord != None, wq.y_coord != None, wq.m_value == None)
	else:
		raise Exception("Input params are not valid.")
	return q


def main(query_type="ALL", overwrite=False, idrange=None, dates=None, updatesites=False):
	"""
	Updates m-values in database by linear reference pts along reference line
	:param query_type: choose "ALL", "IDRANGE", or "DATERANGE"
	:param overwrite: optional - overwrites any existing m values
	:param idrange: when query_type="IDRANGE" range of ids as list where [start_id, end_id]
		Ex: main("IDRANGE", overwrite=True, idrange=[120, 2000])
	:param dates: when query_type="DATERANGE" two datetime objects as list where [start_date, end_date].
		Ex: main("DATERANGE", overwrite=False, dates=[datetime.datetime(2016, 1, 01), datetime.datetime(2016, 1, 31)])
	:param updatesites: boolean - will use the linear reference line to update the sites code
	:return:
	"""
	session = classes.get_new_session()

	if updatesites:
		sites = pullSites(session)
	else:
		sites = None

	try:
		print("Querying Database")
		q = queryBuilder(session, query_type, overwrite, idrange, dates)
		numrecs = q.count()
		print("Number of records returned by query: {}.".format(numrecs))
		if numrecs > 0:
			print("Linear referencing wqt points. Be patient....")

			distances = getMvalues(q, sites)
			print("Updating database...")
			bulk_updateM(session, distances)
			session.commit()
		else:
			print("Query returned zero records to update.")
	finally:
		session.close()
	return


if __name__ == '__main__':
	main("ALL", overwrite=True,  updatesites=True)
