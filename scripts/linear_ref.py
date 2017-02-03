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
	ref_table_out = arcpy.LocateFeaturesAlongRoutes_lr(wq_features, ref_route, "Slough",
                                   "250 Meters", r"in_memory\out_table", out_event_properties="RID POINT MEAS")

	return ref_table_out


def ID_MeasurePair(linear_referenced_table, ID_field):
	"""
	Creates python dict pair with the each records FID and linear measurement along reference line
	:param linear_referenced_table: Table with linear reference results
	:param ID_field: Field name that uniquely identifies the record
	:return: python data dictionary with key = recond FID, value = measurement along line
	"""
	cursor = arcpy.da.SearchCursor(linear_referenced_table, [ID_field, 'MEAS'])
	measurePairs = {}
	for row in cursor:
		measurePairs[row[0]] = row[1]
	return measurePairs


def getMvalues(query):
	"""
	Given a SQLAlchemy query for water quality data, exports a feature class to linear reference which is used to update m_values
	:param query: a SQLAlchemy query object for records to update
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
		distances = ID_MeasurePair(meas_table, "id")

	finally:
		# clean up temp layer
		arcpy.Delete_management(r"in_memory\q_as_layer")

	return distances


def updateM(session, idDistance):
	"""
	Updates the m-values using the id and measurement in the distances dict
	:param session: an open SQLAlchemy database session
	:param idDistance: data dict of water_quality ID and linear ref distance (output of getMvalues)
	:return:
	"""
	# update the selected records in the database with the new measurements
	for location in idDistance.keys():
		record = session.query(classes.WaterQuality).filter(classes.WaterQuality.id == location).one_or_none()
		if record is None:
			# print a warning
			continue  # skip the record - FID not found - likly a problem
		record.m_value = idDistance[location]
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


def main(query_type="ALL", overwrite=False, idrange=None, dates=None):
	"""
	Updates m-values in database by linear reference pts along reference line
	:param query_type: choose "ALL", "IDRANGE", or "DATERANGE"
	:param overwrite: optional - overwrites any existing m values
	:param idrange: when query_type="IDRANGE" range of ids as list where [start_id, end_id]
		Ex: main("IDRANGE", overwrite=True, idrange=[120, 2000])
	:param dates: when query_type="DATERANGE" two datetime objects as list where [start_date, end_date].
		Ex: main("DATERANGE", overwrite=False, dates=[datetime.datetime(2016, 1, 01), datetime.datetime(2016, 1, 31)])
	:return:
	"""
	session = classes.get_new_session()
	try:
		print("Querying Database")
		q = queryBuilder(session, query_type, overwrite, idrange, dates)
		numrecs = q.count()
		if numrecs > 0:
			print("Linear referencing {} wqt points - be patient....".format(numrecs))
			distances = getMvalues(q)
			print("Updating database...")
			updateM(session, distances)
			session.commit()
		else:
			print("Query returned zero records to update.")
	finally:
		session.close()
	return


if __name__ == '__main__':
	main()
