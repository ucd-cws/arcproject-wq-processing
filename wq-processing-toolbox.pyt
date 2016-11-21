import arcpy
import os
import pandas
from scripts import wqt_timestamp_match
from scripts import wq_gain
from scripts import linear_ref

from waterquality import classes

class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
		self.label = "ArcWQ"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [checkmatch, wqt2shp, gain2shp, AddSite, LinearRef, JoinTimestamp]


class AddSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Add New Site"
		self.description = ""
		self.canRunInBackground = False

	def getParameterInfo(self):

		site_name = arcpy.Parameter(
			displayName="Site Name",
			name="site_name",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		site_code = arcpy.Parameter(
			displayName="Site Code",
			name="site_code",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		params = [site_name, site_code]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):

		session = classes.get_new_session()
		try:
			site = classes.Site()
			site.code = parameters[1].valueAsText
			site.name = parameters[0].valueAsText
			session.add(site)
			session.commit()
		finally:
			session.close()


class LinearRef(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Add M distance"
		self.description = "Calculates distance along slough for all water quality measurements along transects"
		self.canRunInBackground = False

	def getParameterInfo(self):

		return

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		arcpy.AddMessage("Updating all records that don't have m_values along slough")
		# creates new session
		session = classes.get_new_session()

		try:
			# temporary table
			table = "in_memory/recs_np_table"

			# turn records that need slough measurement to a table
			linear_ref.data_to_linear_reference(session, table)

			# check that the table exists
			if arcpy.Exists(table):

				# turn table into feature layer using XY coords
				features = linear_ref.makeFeatureLayer(table)

				# locate features along route using the slough reference lines
				meas_table = linear_ref.LocateWQalongREF(features)

				# create data dict with ID and measurement result
				distances = linear_ref.ID_MeasurePair(meas_table, "id")

				# get count of number of records that are going to be updated
				count = len(distances)
				print(arcpy.AddMessage("Number of records updated: {}".format(count)))

				# update the selected records in the database with the new measurements
				for location in distances.keys():
					record = session.query(classes.WaterQuality).filter(
						classes.WaterQuality.id == location).one_or_none()

					if record is None:
						# print a warning
						continue  # skip the record - FID not found - likly a problem - can use .one() instead of .one_or_none() above to raise an exception instead, if no record is found

					record.m_value = distances[location]
			else:
				print(arcpy.AddMessage("No records updated"))

			session.commit()
			arcpy.Delete_management("recs_np_table")
		finally:
			session.close()
		return


class JoinTimestamp(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Transect - Join on Timestamp"
		self.description = "Join water quality transect to gps using time stamp and add to database"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		csvs = arcpy.Parameter(
			displayName="Transect Water Quality Data",
			name="csv_files",
			datatype="DEFile",
			multiValue=True,
			direction="Input"
		)

		# shapefile for the transects GPS breadcrumbs
		bc = arcpy.Parameter(
			displayName="Transect Shapefile",
			name="shp_file",
			datatype="DEFeatureClass",
			direction="Input"
		)

		add = arcpy.Parameter(
			displayName="Add to database?",
			name="add",
			datatype="GPBoolean",
			direction="Input"
		)

		params = [csvs, bc, add]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		param1 = parameters[0].value.exportToString()
		wq_transect_list = param1.split(";")

		transect_gps = str(parameters[1].valueAsText)

		arcpy.AddMessage(transect_gps)

		add2db = parameters[2]

		# list of water quality files from parameter
		#wq = wqt_timestamp_match.wq_append_fromlist(wq_transect_list)
		#wq = wq_transect_list[0] # TODO

		arcpy.AddMessage("Processing Water Quality")
		wq = wqt_timestamp_match.wq_append_fromlist(wq_transect_list)

		arcpy.AddMessage("Processing GPS input")
		pts = wqt_timestamp_match.wqtshp2pd(transect_gps)


		# join using time stamps with exact match
		joined_data = wqt_timestamp_match.JoinByTimeStamp(wq, pts)
		matched = wqt_timestamp_match.splitunmatched(joined_data)[0]

		arcpy.AddMessage("Percent Matched: {}".format(wqt_timestamp_match.JoinMatchPercent(wq, matched)))

		if add2db:
			session = classes.get_new_session()
			wqt_timestamp_match.wq_df2database(matched, session=session)

			tobeadded = len(matched)

			arcpy.AddMessage("Number of records added: {}".format(tobeadded))

			session.commit()
			session.close()
		else:
			arcpy.AddMessage("Fix problems and then add to database")

		return


class checkmatch(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Percent Match - Water Quality data with Transect"
		self.description = "Reports the percent match for multiple water quality dataset with transect shapefile"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		csvs = arcpy.Parameter(
			displayName="Transect Water Quality Data",
			name="wqt_files",
			datatype="DEFile",
			multiValue=True,
			direction="Input"
		)

		# shapefile for the transects GPS breadcrumbs
		bc = arcpy.Parameter(
			displayName="Transect Shapefile",
			name="shp_file",
			datatype="DEShapefile",
			direction="Input"
		)


		params = [csvs, bc]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		param1 = parameters[0].valueAsText
		wq_transect_list = param1.split(";")

		pts = str(parameters[1].valueAsText)
		shp_df = wqt_timestamp_match.wqtshp2pd(pts)

		for wq in wq_transect_list:
			basename = os.path.basename(wq)
			wq_df = wqt_timestamp_match.wq_from_file(wq)
			ts_join = wqt_timestamp_match.JoinByTimeStamp(wq_df, shp_df)
			ts_results = wqt_timestamp_match.splitunmatched(ts_join)
			percent = wqt_timestamp_match.JoinMatchPercent(wq_df, ts_results[0])

			arcpy.AddMessage("{} has a {} % match with the transect. ".format(basename, percent))

		return


class wqt2shp(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Join WQT to SHP"
		self.description = "Matches Water Quality data with Transect using timestamps"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		wq_data = arcpy.Parameter(
			displayName="Transect Water Quality Data (wqt)",
			name="wqt_files",
			datatype="DEFile",
			multiValue=True,
			direction="Input"
		)

		# shapefile for the transects GPS breadcrumbs
		bc = arcpy.Parameter(
			displayName="Transect Shapefile",
			name="shp_file",
			datatype="DEShapefile",
			direction="Input"
		)

		out = arcpy.Parameter(
			displayName="Output Feature Class",
			name="out_file",
			datatype="DEShapefile",
			direction="Output"
		)

		params = [wq_data, bc, out]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""

		# get the parameters
		param1 = parameters[0].valueAsText
		wq_transect_list = param1.split(";") # the multi input needs to be split
		gps_pts = str(parameters[1].valueAsText)
		output_feature = parameters[2].valueAsText

		# see wqt_timestamp_match for functions
		wqt_timestamp_match.main(wq_transect_list, gps_pts, output_feature)

		return


class gain2shp(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Join Gain profile average to SHP"
		self.description = "Matches vertical Water Quality data with Transect using site names"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		wqp = arcpy.Parameter(
			displayName="Vertical Profile file (wqp)",
			name="wqp_files",
			datatype="GPValueTable",
			multiValue=True,
			direction="Input"
		)

		wqp.columns = [['DEFile', 'WQP'], ['GPString', 'Site ID'], ['GPString', 'Gain Type']]
		wqp.filters[1].type = 'ValueList'
		wqp.filters[1].list = ['BK1', 'CA1', 'CA3', 'CC1', 'LNCA', 'UL1']  # TODO fill in from file name?
		wqp.filters[2].type = 'ValueList'
		wqp.filters[2].list = ['g0', 'g1', 'g10', 'g100']


		# shapefile for the stationary GPS points
		bc = arcpy.Parameter(
			displayName="WQP/Zoop/Chl Shapefile",
			name="shp_file",
			datatype="DEShapefile",
			direction="Input"
		)

		out = arcpy.Parameter(
			displayName="Output Feature Class",
			name="out_file",
			datatype="DEShapefile",
			direction="Output"
		)

		params = [wqp, bc, out]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		# get the parameters
		param = parameters[0].valueAsText
		file_params = param.split(";") # the multi input needs to be split
		wqps = []
		for f in file_params:
			# MAKE SURE FILE does not have spaces!!!!
			row = f.split(" ") # split using single space
			wqps.append(row)

		arcpy.AddMessage(wqps)

		gps_pts = str(parameters[1].valueAsText)
		output_feature = parameters[2].valueAsText

		master_wq_df = pandas.DataFrame()  # temporary df to store the results from the individual inputs

		for wq in wqps:
			wq_gain_file = wq[0]
			site_id = wq[1]
			gain_setting = wq[2]

			join_df = wq_gain.main(wq_gain_file, gps_pts, site_id, gain_setting)

			# append to master wq
			master_wq_df = master_wq_df.append(join_df)

		arcpy.AddMessage(master_wq_df.head())

		# Save the gain results to a shapefile
		# Define a spatial reference for the output feature class by copying the input
		spatial_ref = arcpy.Describe(gps_pts).spatialReference

		# convert pandas dataframe to structured numpy array
		match_np = wqt_timestamp_match.pd2np(master_wq_df)

		# convert structured array to output feature class
		wqt_timestamp_match.np2feature(match_np, output_feature, spatial_ref)

		return
