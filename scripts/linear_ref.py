# linear reference points along sloughs
# given x, y and slough name return distance along slough
import arcpy
import os
from waterquality import classes
import numpy as np
import wqt_timestamp_match

# reference routes that are used to get the slough distance
wd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ref_routes = os.path.join(wd, "geo", "Reference_SloughCenterlines.shp")  # routes as lines


def data_to_linear_reference(session, query, in_memory_table):
	"""
	Turns records from session query into an arcgis table
	:param session: session
	:param query: a query that returns all the records that should be updated with m_values
	:param in_memory_table: name of table to create in memory
	:return:
	"""
	# if the query is empty than all records have values
	if len(q) == 0:
		print("All records with Lat/Long have m_values.")
	else:
		recs = []

		# iterate through records pulling just the id, lat, and long
		for record in q:
			row = [record.id, record.y_coord, record.x_coord]
			recs.append(row)

		# turn lists of records to numpy array to table
		dts = {'names': ('id', 'y_coord', 'x_coord'),
		            'formats': (np.dtype(int), np.float64, np.float64)}
		array = np.rec.fromrecords(recs, dtype=dts)

		# save numpy array to table
		arcpy.da.NumPyArrayToTable(array, in_memory_table)

	return


def subset_ref_route(reference_lines, slough):
	# TODO select by reach name so that points at confluences get assigned properly
	pass


def makeFeatureLayer(table):
	"""
	Turns a table with Point_X and Point_Y fields (in CA teale albers) into feature layer in memory
	:param table: input table with X and Y coordinates stored in field (ie not stored in spatial db)
	:return: feature class stored in memory
	"""

	if arcpy.Exists("temp_layer"):
		arcpy.Delete_management("temp_layer")

	if arcpy.Exists(r"in_memory\out_layer"):
		arcpy.Delete_management(r"in_memory\out_layer")

	# spatial reference
	sr = arcpy.SpatialReference(wqt_timestamp_match.projection_spatial_reference)

	# create XY event layer using the Point_X and Point_Y fields from the table
	arcpy.MakeXYEventLayer_management(table,  "x_coord", "y_coord", "temp_layer", spatial_reference=sr)
	try:
		# the XY event layer  does not have a object ID - need to copy to disk via in_memory
		out_layer = arcpy.CopyFeatures_management("temp_layer", r"in_memory\out_layer")
	finally:
		# removes the XY event layer
		arcpy.Delete_management("temp_layer")  # delete the temp layer

	return out_layer


def LocateWQalongREF(wq_features):
	"""
	Uses arcpy linear refereeing to locate the input features distances along the reference route
	:param wq_features: water quality transect points as feature class
	:return: table with measurement along line, distance to ref line, etc.
	"""
	#  use linear referencing to locate each point along route using arcgis's linear referencing tool set

	# note wq_feature needs to FID/OID
	ref_table_out = arcpy.LocateFeaturesAlongRoutes_lr(wq_features, ref_routes, "Slough",
                                   "250 Meters", r"in_memory\out_table", out_event_properties="RID POINT MEAS")

	return ref_table_out


def ID_MeasurePair(linear_referenced_table, ID_field):
	"""
	Creates python dict pair with the each records FID and linear measurement along reference line
	:param linear_referenced_table: Table with linear reference results
	:param ID_field: Field name that uniquely identifies the record
	:return: python data dictionary with key = recond FID, value = measurement along line
	"""

	# returns data table with input FID, distance along route (MEAS) and distance from the line
	cursor = arcpy.da.SearchCursor(linear_referenced_table, [ID_field, 'MEAS'])

	measurePairs = {}

	for row in cursor:
		print(row)
		measurePairs[row[0]] = row[1]

	return measurePairs


def main():
	"""
	Updates all the records with null m_values in the waterquality table
	:return:
	"""

	# creates new session
	session = classes.get_new_session()

	# Return all the records that do not have m values
	q = session.query(classes.WaterQuality).filter(classes.WaterQuality.m_value == None,
			classes.WaterQuality.y_coord != None, classes.WaterQuality.x_coord != None ).all()

	try:
		# turn records that need slough measurement to a table
		data_to_linear_reference(session, q, "in_memory/recs_np_table")

		# check that the table exists
		if arcpy.Exists("in_memory/recs_np_table"):

			# turn table into feature layer using XY coords
			print("Creating XY table")
			features = makeFeatureLayer("in_memory/recs_np_table")

			# locate features along route using the slough reference lines
			print("Locating Features along routes")
			meas_table = LocateWQalongREF(features)

			# create data dict with ID and measurement result
			distances = ID_MeasurePair(meas_table, "id")

			print("Updating records")
			# update the selected records in the database with the new measurements
			for location in distances.keys():
				record = session.query(classes.WaterQuality).filter(classes.WaterQuality.id == location).one_or_none()

				if record is None:
					# print a warning
					continue  # skip the record - FID not found - likly a problem - can use .one() instead of .one_or_none() above to raise an exception instead, if no record is found

				record.m_value = distances[location]
		else:
			print("No records updated")

		session.commit()

	finally:
		session.close()

if __name__ == '__main__':
	main()
