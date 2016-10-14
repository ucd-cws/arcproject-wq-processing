import arcpy
import os
from scripts import wqt_timestamp_match

class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
		self.label = "ArcWQ"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [JoinTimestamp]


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
