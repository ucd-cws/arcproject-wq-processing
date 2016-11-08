# linear reference points along sloughs
# given x, y and slough name return distance along slough
import arcpy
import os

# reference routes that are used to get the slough distance
wd = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ref_points = os.path.join(wd, "geo", "Reference_SloughCenterlines_asPoints.shp")  # routes as points spread out approx every 1m
ref_routes = os.path.join(wd, "geo", "Reference_SloughCenterlines.shp")  # routes as lines


def data_to_linear_reference(dbase, some_query):

	# not sure the format of this yet but likely it with be a list of database rows with XY
	pass


# TODO select by reach name so that points at confluences get assigned properly



def makeFeatureLayer(table):
	# spatial reference
	sr = arcpy.SpatialReference(3310)  # CA teale albers ESPG code
	arcpy.MakeXYEventLayer_management(table, "Point_X", "Point_Y", "temp_layer", spatial_reference=sr)

	# the XY event layer  does not have a object ID - need to copy to disk via in_memory
	out_layer = arcpy.CopyFeatures_management("temp_layer", r"in_memory\out_layer")

	arcpy.Delete_management("temp_layer") # delete the temp layer

	return out_layer



def LocateWQalongREF(wq_features):
	#  use linear referencing to locate each point along route using arcgis's linear referencing tool set

	# note wq_feature needs to FID/OID
	ref_table_out = arcpy.LocateFeaturesAlongRoutes_lr(wq_features, ref_routes, "Slough",
                                   "250 Meters", r"in_memory\out_table", out_event_properties="RID POINT MEAS")

	return ref_table_out


def ID_MeasurePair(linear_referenced_table, ID_field):
	# returns data table with input FID, distance along route (MEAS) and distance from the line
	cursor = arcpy.da.SearchCursor(linear_referenced_table, [ID_field, 'MEAS'])

	measurePairs = {}

	for row in cursor:
		print(row)
		measurePairs[row[0]] = row[1]

	return measurePairs


# test files

# csv = os.path.join(wd, "geo", "tests", "test_wq_pts_csv.csv")
#
# test_make = makeFeatureLayer(csv)
#
# ref_table_out = LocateWQalongREF(test_make)
#
# pairs = ID_MeasurePair(ref_table_out, "FID")
#
# print(pairs)


def clean_up():
	#arcpy.Delete_management(featureLayer)
	pass



def update_table_river_distance(dbase, table, fids_w_RM):

	# function to update the selected rows in the table with the appropriate distance along the route.

	pass