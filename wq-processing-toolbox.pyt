import arcpy
import os
import pandas
from scripts import wqt_timestamp_match
from scripts import wq_gain
from scripts import mapping
from sqlalchemy import exc
from waterquality import classes

from datetime import timedelta

class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
		self.label = "ArcWQ"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [CheckMatch, GenerateWQLayer, GainToDB, AddSite, JoinTimestamp, AddGainSite]

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


class GenerateWQLayer(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Generate Map Layer from Water Quality Data"
		self.description = ""
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		date_to_generate = arcpy.Parameter(
			displayName="Date to Generate Layer For",
			name="date_to_generate",
			datatype="GPDate",
			multiValue=False,
			direction="Input"
		)

		# shapefile for the transects GPS breadcrumbs
		fc = arcpy.Parameter(
			displayName="Output Feature Class",
			name="output_feature_class",
			datatype="DEFeatureClass",
			direction="Output"
		)

		params = [date_to_generate, fc, ]
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
		date_to_use = parameters[0].value
		output_location = parameters[1].valueAsText

		wq = classes.WaterQuality
		session = classes.get_new_session()

		arcpy.AddMessage("Using Date {}".format(type(date_to_use)))

		upper_bound = date_to_use.date() + timedelta(days=1)

		query = session.query(wq).filter(wq.date_time > date_to_use.date(), wq.date_time < upper_bound, wq.x_coord != None, wq.y_coord != None)  # add 1 day's worth of nanoseconds
		mapping.query_to_features(query, output_location)


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



class GainToDB(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Add Gain profile to database"
		self.description = "Takes average of water quality parameters of the top 1m of the vertical profile"
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

		bool = arcpy.Parameter(
			displayName="Fill in table by parsing filename?",
			name="bool",
			datatype="GPBoolean"
		)

		# shapefile for the stationary GPS points
		shp = arcpy.Parameter(
			displayName="Shapefile with Vertical Profile Locations",
			name="shp_file",
			datatype="GPFeatureLayer",
			direction="Input",
			parameterType="Optional"
		)

		params = [wqp, bool, shp]
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
				profiles = session.query(classes.ProfileSite.abbreviation).distinct().all()
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
		gps_pts = parameters[2].value
		arcpy.AddMessage(gps_pts)

		for i in range(0, len(vt)):

			wq_gain_file = str(vt[i][0])
			basename = os.path.basename(str(wq_gain_file))
			vt[i][0] = str(wq_gain_file)
			site_id = vt[i][1] # site
			gain_setting = vt[i][2] # gain
			arcpy.AddMessage("{} {} {}".format(basename, site_id, gain_setting))

			wq_gain.main(wq_gain_file, site_id, gain_setting, gps_pts)

		return


class AddGainSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "New Vertical Gain Profile Sites"
		self.description = ""
		self.canRunInBackground = False

	def getParameterInfo(self):

		ZoopChlW = arcpy.Parameter(
			displayName="Vertical Profile GPS points",
			name="ZoopChlW",
			datatype="GPFeatureLayer",
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

		params = [ZoopChlW, site_codes]
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

		# linear reference to get the slough id and m_value

		# iterate through rows and add to profile sites
		cursor = arcpy.da.SearchCursor(feature_class, [profile_field, "SHAPE@Y", "SHAPE@X"])
		for row in cursor:
			ps = classes.ProfileSite()
			arcpy.AddMessage(row)
			ps.abbreviation = row[0]
			ps.y_coord = row[1]
			ps.x_coord = row[2]

			# add to db
			session = classes.get_new_session()
			try:
				session.add(ps)
				session.commit()
			except exc.IntegrityError as e:
				arcpy.AddMessage(e)
				arcpy.AddMessage("{} already exists. Skipping.".format(ps.abbreviation))
			finally:
				session.close()

		# TODO add m_value (maybe add to lin ref tool function?)
