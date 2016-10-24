import arcpy
import os
import pandas
from scripts import wqt_timestamp_match

class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
		self.label = "ArcWQ"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [checkmatch, wqt2shp, gain2shp]


class JoinTimestamp(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Join on Timestamp"
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

		out = arcpy.Parameter(
			displayName="Joined Output",
			name="Output",
			datatype="DEFeatureClass",
			direction="Output"
		)

		params = [csvs, bc, out]
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

		pts = arcpy.GetParameterAsText(1)
		arcpy.AddMessage(pts)

		out = arcpy.GetParameterAsText(2)

		# list of water quality files from parameter
		#wq = wqt_timestamp_match.wq_append_fromlist(wq_transect_list)
		wq = wq_transect_list[0] # TODO

		# run wq_join_match
		wqt_timestamp_match.main(wq, pts, out)

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
			parameterType='Required',
			multiValue=True,
			direction="Input"
		)

		wqp.columns = [['DEFile', 'WQP'], ['GPString', 'Site ID'], ['GPString', 'Gain Type']]
		wqp.filters[1].type = 'ValueList'
		wqp.filters[1].list = ['BK1', 'CA1', 'CA3', 'CC1', 'LNCA', 'UL1']
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
		arcpy.AddMessage(parameters[0])
		# get the parameters
		param = parameters[0].valueAsText
		file_params = param.split(";") # the multi input needs to be split
		wqp = []
		for f in file_params:
			arcpy.AddMessage(f)
			# MAKE SURE FILE does not have spaces!!!!
			row = f.split(" ") # split using single space
			arcpy.AddMessage(row)
			wqp.append(row)

		arcpy.AddMessage(wqp)



		# gps_pts = str(parameters[1].valueAsText)
		# output_feature = parameters[2].valueAsText
		#
		# # see wqt_timestamp_match for functions
		# wqt_timestamp_match.main(wq_transect_list, gps_pts, output_feature)
		pass

		return