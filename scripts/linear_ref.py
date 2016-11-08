# linear reference points along sloughs
# given x, y and slough name return distance along slough
import arcpy
import os
from waterquality import classes

# reference routes that are used to get the slough distance
wd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ref_routes = os.path.join(wd, "geo", "Reference_SloughCenterlines.shp")  # routes as lines


def data_to_linear_reference(session, some_query):
	# not sure the format of this yet but likely it with be a list of database rows with XY
	pass


def subset_ref_route():
	# TODO select by reach name so that points at confluences get assigned properly
	pass


def makeFeatureLayer(table):
	"""
	Turns a table with Point_X and Point_Y fields (in CA teale albers) into feature layer in memory
	:param table: input table with X and Y coordinates stored in field (ie not stored in spatial db)
	:return: feature class stored in memory
	"""

	# spatial reference
	sr = arcpy.SpatialReference(3310)  # CA teale albers ESPG code

	# create XY event layer using the Point_X and Point_Y fields from the table
	arcpy.MakeXYEventLayer_management(table, "Point_X", "Point_Y", "temp_layer", spatial_reference=sr)
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


def update_table_river_distance(dbase, table, fids_w_RM):

	# function to update the selected rows in the table with the appropriate distance along the route.

	pass


def main(records_to_update):

	session = classes.get_new_session()

	try:
		# turn records that need slough measurement to a table
		table = data_to_linear_reference(records_to_update)

		# turn table into feature layer using XY coords
		features = makeFeatureLayer(table)

		# locate features along route using the slough reference lines
		meas_table = LocateWQalongREF(features)

		# create data dict with ID and measurement result
		distances = ID_MeasurePair(meas_table)

		# update the selected records in the databae with the new measurements
		#update_table_river_distance()

		session.commit()

	finally:
		session.close()
