import arcpy
import os
import pandas
from scripts import wqt_timestamp_match
from scripts import wq_gain

from waterquality import classes

class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
		self.label = "ArcWQ"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [CheckMatch, WqtToShapefiile, GainToShapefile, AddSite, JoinTimestamp]


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


class JoinTimestamp(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Add Water Quality Data to Database"
		self.description = ""
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


class GainToShapefile(object):
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
