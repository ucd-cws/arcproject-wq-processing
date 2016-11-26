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
		self.tools = [CheckMatch, WqtToShapefiile, GainToDB, AddSite, JoinTimestamp, AddGainSite]

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

		site = arcpy.Parameter(
			displayName="Site Code (Leave blank to detect from filename)",
			name="site_code",
			datatype="GPString",
			direction="Input",
			parameterType="Optional",
		)

		out = arcpy.Parameter(
			displayName="Joined Output",
			name="Output",
			datatype="DEFeatureClass",
			direction="Output",
			parameterType="Optional"
		)

		params = [csvs, bc, site, out]

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
		wq_transect_list = parameters[0].value

		pts = parameters[1].valueAsText
		arcpy.AddMessage(pts)

		site_code = parameters[2].valueAsText
		if not site_code or site_code == "":
			site_function = wqt_timestamp_match.site_function_historic

		output_path = parameters[3].valueAsText
		if output_path == "":
			output_path = None

		# run wq_join_match
		wqt_timestamp_match.main(wq_transect_list, pts, output_feature=output_path, site_function=site_function)

		if output_path:
			parameters[3].value = output_path
			pass


class CheckMatch(object):
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
		wq_transect_list = parameters[0].value

		transect_gps = str(parameters[1].valueAsText)

		arcpy.AddMessage(transect_gps)

		add2db = parameters[2]

		# list of water quality files from parameter
		# wq = wqt_timestamp_match.wq_append_fromlist(wq_transect_list)
		# wq = wq_transect_list[0] # TODO

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


class WqtToShapefiile(object):
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


class GainToDB(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Add Gain profile average to database"
		self.description = "Matches vertical Water Quality data with Transect using site names"
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		wqp = arcpy.Parameter(
			displayName="Vertical Profile file (wqp)",
			name="wqp_files",
			parameterType="GPValueTable",
			multiValue=True,
			direction="Input"
		)

		wqp.columns = [['DEFile', 'WQP'], ['GPString', 'Site ID'], ['GPString', 'Gain Type']]

		# TODO get list of gain settings from the data base?
		wqp.filters[2].type = 'ValueList'
		wqp.filters[2].list = ['0', '1', '10', '100']


		# shapefile for the stationary GPS points
		bc = arcpy.Parameter(
			displayName="WQP/Zoop/Chl Shapefile",
			name="shp_file",
			datatype="DEShapefile",
			direction="Input"
		)

		bool = arcpy.Parameter(
			displayName="Fill in table by parsing filename?",
			name="bool",
			datatype="GPBoolean"
		)

		params = [wqp, bool, bc]
		return params


	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		if parameters[0].valueAsText:

			# validate site name by pulling creating filter with names from profile_sites table
			# get list of sites from the database profile sites table
			session = classes.get_new_session()
			try:
				profiles = session.query(classes.ProfileSite.profile_name).distinct().all()
				# print(profiles)  # [(u'TES1',), (u'TES2',), (u'TS1',)]
				profile_names = []

				# add profile name to site list
				for profile in profiles:
					print(profile[0])
					profile_names.append(profile[0])

				parameters[0].filters[1].type = 'ValueList'
				parameters[0].filters[1].list = profile_names

			finally:
				session.close()

		# updates the value table using the values parsed from the file name
		if parameters[1].value:
			vt = parameters[0].values # values are list of lists

			for i in range(0, len(vt)):
				filename = vt[i][0]
				basename = os.path.basename(str(filename))
				base = os.path.splitext(basename)[0]  # rm extension if there is one
				parts = base.split("_")  # split on underscore
				site = parts[2]
				gain = parts[4]
				vt[i][0] = str(filename)
				vt[i][1] = site
				vt[i][2] = gain
			parameters[0].values = vt

			# set checkbox to false
			parameters[1].value = False

		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		# get the parameters

		vt = parameters[0].values  # values are list of lists
		gps_pts = str(parameters[2].valueAsText)

		master_wq_df = pandas.DataFrame()  # temporary df to store the results from the individual inputs

		for i in range(0, len(vt)):

			wq_gain_file = str(vt[i][0])
			basename = os.path.basename(str(wq_gain_file))
			vt[i][0] = str(wq_gain_file)
			site_id = vt[i][1] # site
			gain_setting = vt[i][2] # gain
			arcpy.AddMessage("{} {} {}".format(basename, site_id, gain_setting))

			join_df = wq_gain.main(wq_gain_file, gps_pts, site_id, gain_setting)
			master_wq_df = master_wq_df.append(join_df)



		arcpy.AddMessage(master_wq_df.head())

		# TODO append the pandas data frame to the database table

		return


class AddGainSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Add Vertical Gain Profile Site"
		self.description = ""
		self.canRunInBackground = False

	def getParameterInfo(self):

		ZoopChlW = arcpy.Parameter(
			displayName="Vertical Profile GPS points",
			name="ZoopChlW",
			datatype="DEShapefile",
			multiValue=False,
			direction="Input"
		)

		site_codes = arcpy.Parameter(
			displayName="Field with site codes",
			name="site_codes",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		sloughs = arcpy.Parameter(
			displayName="Transect Code",
			name="transect_code",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		params = [ZoopChlW, site_codes, sloughs]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		# populate the field selection using the fields from the shapefile
		if parameters[0].value:
			parameters[1].filter.list = [f.name for f in arcpy.Describe(parameters[0].value).fields]
			parameters[2].filter.list = [f.name for f in arcpy.Describe(parameters[0].value).fields]

		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):

		# project to CA teale albers
		feature_class = parameters[0].valueAsText
		desc = arcpy.Describe(feature_class)
		try:
			if desc.spatialReference.factoryCode != 3310:
				feature_class = wqt_timestamp_match.reproject_features(feature_class)
		finally:
			del desc

		profile_field = parameters[1].valueAsText
		transect_field = parameters[2].valueAsText

		# iterate through rows and add to profile sites
		cursor = arcpy.da.SearchCursor(feature_class, [profile_field, transect_field, "SHAPE@Y", "SHAPE@X"])
		for row in cursor:
			ps = classes.ProfileSite()
			arcpy.AddMessage(row)
			ps.abbreviation = row[0]
			ps.latitude = row[2]
			ps.longitude = row[3]

			arcpy.AddMessage(ps)

		# check that profile site does not already exist

		# TODO add m_value (maybe add to lin ref tool function?)


		# session = classes.get_new_session()
		# try:
		# 	site = classes.Site()
		# 	site.code = parameters[1].valueAsText
		# 	site.name = parameters[0].valueAsText
		# 	session.add(site)
		# 	session.commit()
		# finally:
		# 	session.close()
