import calendar
import datetime
import os
import shutil
import subprocess
import time
import webbrowser
import csv
from functools import wraps
from string import digits

import arcpy
from sqlalchemy import exc, func, distinct, extract

import amaptor
import geodatabase_tempfile
import launchR

from arcproject.scripts import chl_decision_tree
from arcproject.scripts import config
from arcproject.scripts import linear_ref
from arcproject.scripts import mapping
from arcproject.scripts import swap_site_recs
from arcproject.scripts import wq_gain
from arcproject.scripts import wqt_timestamp_match
from arcproject.scripts.mapping import generate_layer_for_month, WQMappingBase
from arcproject.waterquality import classes


def parameters_as_dict(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		params = args[1]
		parameters = {}
		for param in params:
			parameters[param.name] = param

		f(self=args[0], parameters=parameters, messages=args[1])

	return wrapper


class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
		self.label = "ArcProject WQ Toolbox"
		self.alias = "ArcProject WQ Toolbox"
		# List of tool classes associated with this toolbox
		self.tools = [AddSite, AddGainSite, JoinTimestamp,
		              GenerateWQLayer, GainToDB, GenerateMonth, ModifyWQSite, GenerateHeatPlot,
		              GenerateSite, ModifySelectedSite, GenerateMap, DeleteMonth, LinearRef, RenameGrabs,
		              RegressionPlot, CorrectChl, ExportHeatPlotData]


class AddSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "New Transect Site"
		self.description = "Add a new water quality transect site to the database. Each slough should have it's own unique site id."
		self.canRunInBackground = False
		self.category = "Create New Sites"

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
			site.code = parameters[1].valueAsText.upper()
			site.name = parameters[0].valueAsText
			session.add(site)
			session.commit()
		except exc.IntegrityError as e:
			arcpy.AddMessage("{} already exists. Site IDs must be unique.".format(site.code))
		finally:
			session.close()


class AddGainSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "New Profile Site"
		self.description = "Create a new vertical profile site"
		self.canRunInBackground = False
		self.category = "Create New Sites"

	def getParameterInfo(self):

		abbr = arcpy.Parameter(
			displayName="Profile Abbreviation",
			name="abbr",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		slough = arcpy.Parameter(
			displayName="Transect?",
			name="slough",
			datatype="GPString",
			multiValue=False,
			direction="Input",
			parameterType="Optional",
		)

		params = [abbr, slough]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		# fill in the sloughs with options already in the database
		if parameters[0].valueAsText:
			session = classes.get_new_session()
			try:
				q = session.query(classes.Site.code).distinct().all()
				sites = []
				# add profile name to site list
				for site in q:
					print(site[0])
					sites.append(site[0])
				parameters[1].filter.type = 'ValueList'
				parameters[1].filter.list = sites
			finally:
				session.close()
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	@parameters_as_dict
	def execute(self, parameters, messages):

		abbr = parameters["abbr"].valueAsText
		slough = parameters["slough"].valueAsText
		ps = classes.ProfileSite()
		ps.abbreviation = abbr.upper()

		if slough is not None:
			ps.slough = slough.upper()

		# add to db
		session = classes.get_new_session()
		try:
			session.add(ps)
			session.commit()
		except exc.IntegrityError as e:
			arcpy.AddMessage("{} already exists. Skipping.".format(ps.abbreviation))
		finally:
			session.close()


class JoinTimestamp(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Add Transects"
		self.description = "Join water quality transect to gps using time stamp and add to database"
		self.canRunInBackground = False
		self.category = "Add WQ Data"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		wqt = arcpy.Parameter(
			displayName="Transect Water Quality Data",
			name="wqt",
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

		params = [wqt, bc, site, out]

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
		wq_transect_list = parameters[0].valueAsText.split(";")

		pts = parameters[1].valueAsText

		site_code = parameters[2].valueAsText
		if not site_code or site_code == "":
			site_function = wqt_timestamp_match.site_function_historic
		else:
			site_function = site_code

		output_path = parameters[3].valueAsText
		if output_path == "":
			output_path = None

		# run wq_join_match
		wqt_timestamp_match.main(wq_transect_list, pts, output_feature=output_path, site_function=site_function)

		pass


class GainToDB(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Add Gain Profiles"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Add WQ Data"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		wqp = arcpy.Parameter(
			displayName="Vertical Profile File",
			name="wqp_files",
			parameterType="GPValueTable",
			multiValue=True,
			direction="Input"
		)

		wqp.columns = [['DEFile', 'Filename'], ['GPString', 'Site ID'], ['GPString', 'Gain Type']]

		# TODO get list of gain settings from the data base?
		wqp.filters[2].type = 'ValueList'
		wqp.filters[2].list = ['0', '1', '10', '100']

		bool = arcpy.Parameter(
			displayName="Fill in table by parsing filename?",
			name="bool",
			datatype="GPBoolean",
			parameterType="Optional"
		)

		# site_part = arcpy.Parameter(
		# 	displayName="Part of filename with site code (split by underscores)?",
		# 	name="site",
		# 	datatype="GPLong",
		# 	parameterType="Optional"
		# )
		#
		# site_part.value = 3
		# site_part.filter.type = "ValueList"
		# site_part.filter.list = [1, 2, 3, 4, 5, 6]
		#
		#
		# gain_part = arcpy.Parameter(
		# 	displayName="Part of filename with gain code (split by underscores)?",
		# 	name="gain",
		# 	datatype="GPLong",
		# 	parameterType="Optional"
		# )
		#
		# gain_part.value = 5
		# gain_part.filter.type = "ValueList"
		# gain_part.filter.list = [1, 2, 3, 4, 5, 6]

		params = [wqp, bool,]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""
		if parameters[0].valueAsText and len(parameters[0].filters[1].list) == 0:

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
			vt = parameters[0].values  # values are list of lists

			for i in range(0, len(vt)):
				filename = vt[i][0]
				basename = os.path.basename(str(filename))
				base = os.path.splitext(basename)[0]  # rm extension if there is one
				parts = base.split("_")  # split on underscore

				#site = parts[int(parameters[2].value)-1]
				site = parts[wqt_timestamp_match.site_function_params.get('site_part')]
				#gain = parts[int(parameters[3].value)-1]
				gain = parts[wqt_timestamp_match.site_function_params.get('gain_part')]
				vt[i][0] = str(filename)
				vt[i][1] = site

				# strip all letters from gain setting ("GN10" -> 10)
				digits_only = ''.join(c for c in gain if c in digits)
				gain = int(digits_only)
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

		for i in range(0, len(vt)):

			wq_gain_file = str(vt[i][0])
			basename = os.path.basename(str(wq_gain_file))
			vt[i][0] = str(wq_gain_file)
			site_id = vt[i][1] # site
			gain_setting = vt[i][2] # gain
			arcpy.AddMessage("{} {} {}".format(basename, site_id, gain_setting))

			try:
				wq_gain.main(wq_gain_file, site_id, gain_setting)
			except exc.IntegrityError as e:
				arcpy.AddMessage("Unable to import gain file. Record for this gain file "
				                 "already exists in the vertical_profiles table.")
		return


class GenerateWQLayer(WQMappingBase):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Map Layer - Single Day"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Mapping"

		super(GenerateWQLayer, self).__init__()

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

		fc = mapping.set_output_symbology(fc)
		params = [date_to_generate, self.select_wq_param, fc, ]
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
		arcpy.env.addOutputsToMap = True
		date_to_use = parameters[0].value
		output_location = parameters[2].valueAsText
		arcpy.AddMessage("Output Location: {}".format(output_location))
		mapping.layer_from_date(date_to_use, output_location)

		self.insert_layer(output_location, parameters[1])


class GenerateMonth(WQMappingBase):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Map Layer - Full Month"
		self.description = "Generate a layer of all the water quality transects for a given month and year"
		self.canRunInBackground = False
		self.category = "Mapping"
		
		super(GenerateMonth, self).__init__()

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files

		# shapefile for the transects GPS breadcrumbs
		fc = arcpy.Parameter(
			displayName="Output Feature Class",
			name="output_feature_class",
			datatype="DEFeatureClass",
			direction="Output"
		)

		params = [self.year_to_generate, self.month_to_generate, self.select_wq_param, fc, ]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		self.update_month_fields(parameters)

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		try:
			arcpy.env.addOutputsToMap = True
			year_to_use, month_to_use = self.convert_year_and_month(year=parameters[0], month=parameters[1])

			arcpy.AddMessage("YEAR: {}, MONTH: {}".format(year_to_use, month_to_use))

			output_location = parameters[3].valueAsText

			generate_layer_for_month(month_to_use, year_to_use, output_location)

			self.insert_layer(output_location, parameters[2])
		finally:
			self.cleanup()  # clean up from tool setup


class GenerateMap(WQMappingBase):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""

		# call the setup first, because we want to overwrite the labels, etc
		super(GenerateMap, self).__init__()

		self.label = "Generate Map for Export"
		self.description = "Generates a map document and optional static image/PDF maps for symbolized water quality data for a month"
		self.canRunInBackground = False
		self.category = "Mapping"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		### There may not be a type for this in Pro, so we should not add the parameter, and instead add a new map in the CURRENT document
		if amaptor.PRO:
			map_output = arcpy.Parameter(
				displayName="Name of New Map in Current Project",
				name="output_map",
				datatype="GPString",
				direction="Output"
			)
		else:  # using ArcMap
			map_output = arcpy.Parameter(
				displayName="Output ArcGIS Map Location",
				name="output_map",
				datatype="DEMapDocument",
				direction="Output"
			)

		export_pdf = arcpy.Parameter(
				displayName="Output Path for PDF",
				name="output_pdf",
				datatype="DEFile",
				direction="Output",
				parameterType="Optional",
				category="Static Map Exports",
			)

		export_png = arcpy.Parameter(
				displayName="Output Path for PNG",
				name="output_png",
				datatype="DEFile",
				direction="Output",
				parameterType="Optional",
				category="Static Map Exports",
			)

		params = [self.year_to_generate, self.month_to_generate, self.select_wq_param, map_output, export_pdf, export_png]

		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		self.update_month_fields(parameters)

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""
			Generates the map and exports any necessary static maps
		:param parameters:
		:return:
		"""
		try:
			arcpy.env.addOutputsToMap = False
			year_to_use, month_to_use = self.convert_year_and_month(year=parameters[0], month=parameters[1])
			symbology_param = parameters[2]

			template = mapping.arcgis_10_template
			output_map_path = parameters[3].valueAsText
			output_pdf_path = parameters[4].valueAsText
			output_png_path = parameters[5].valueAsText
			new_layout_name = "{} Layout".format(output_map_path)
			if amaptor.PRO:
				if "testing_project" in globals(): # this is a hook for our testing code to set a value in the module and have this use it instead of "CURRENT"
					project = globals()["testing_project"]
				else:
					project = "CURRENT"
				map_project = amaptor.Project(project)
				new_map = map_project.new_map(name=output_map_path, template_map=template, template_df_name="ArcProject Map")
				new_layout = map_project.new_layout(name=new_layout_name, template_layout=mapping.arcgis_pro_layout_template, template_name="base_template")
				new_layout.frames[0].map = new_map  # rewrite the data frame map to be the map object of the new map

				output_location = geodatabase_tempfile.create_gdb_name(name_base="generated_month_layer", gdb=map_project.primary_document.defaultGeodatabase)
			else:
				shutil.copyfile(template, output_map_path)
				map_project = amaptor.Project(output_map_path)
				new_map = map_project.maps[0]  # it'll be the first map, because it's the only data frame in the template

				output_location = geodatabase_tempfile.create_gdb_name(name_base="generated_month_layer")

			arcpy.AddMessage("Map Document set up complete. Creating new layer")
			generate_layer_for_month(month_to_use, year_to_use, output_location)

			self.insert_layer(output_location, symbology_param, map_or_project=new_map)
			new_layer = new_map.find_layer(path=output_location)
			new_layer.name = symbology_param.valueAsText
			new_map.zoom_to_layer(layer=new_layer, set_layout="ALL")
			new_map.replace_text("{wq_month}", "{} {}".format(parameters[1].valueAsText, parameters[0].valueAsText))  # Add the month and year to the title
			map_project.save()

			if output_png_path and output_png_path != "":
				new_map.export_png(output_png_path, resolution=300)
			if output_pdf_path and output_pdf_path != "":
				new_map.export_pdf(output_pdf_path)

			if amaptor.PRO:
				arcpy.AddMessage("Look for a new map named \"{}\" and a new layout named \"{}\" in your Project pane".format(output_map_path, new_layout_name))

		finally:
			self.cleanup()  # clean up from tool setup



class ModifyWQSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Swap Transect Code for ALL records"
		self.description = "Modifies the transect code for all records that currently belong to a certain site."
		self.canRunInBackground = False
		self.category = "Modify"

	def getParameterInfo(self):

		current_code = arcpy.Parameter(
			displayName="Current Site Code for records",
			name="site_code",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		new_code = arcpy.Parameter(
			displayName="New Site Code to Assign",
			name="new_code",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		rm = arcpy.Parameter(
			displayName="Remove site from sites table?",
			name="rm",
			datatype="GPBoolean",
			direction="Input",
			parameterType="Optional",
		)

		params = [current_code, new_code, rm]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		# validate site name by pulling creating filter with names from table
		# get list of sites from the database profile sites table
		session = classes.get_new_session()
		try:
			sites = session.query(classes.Site.code).distinct().all()
			site_names = []

			# add profile name to site list
			for s in sites:
				site_names.append(s[0])

			parameters[0].filter.type = 'ValueList'
			parameters[0].filter.list = site_names

			# TODO if parameter[0] has value pop from the list for parameter[1] since it would map to self.
			parameters[1].filter.type = 'ValueList'
			parameters[1].filter.list = site_names

		finally:
			session.close()
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		current_code = parameters[0].value
		new_code = parameters[1].value
		bool_rm = parameters[2].value
		arcpy.AddMessage("Changing records with {} -> {}".format(current_code, new_code))
		c = swap_site_recs.main(current_code, new_code, bool_rm)
		arcpy.AddMessage("{} records updated".format(c))
		return


class GenerateHeatPlot(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Generate Heatplot"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Mapping"

	def getParameterInfo(self):

		code = arcpy.Parameter(
			displayName="Code for Transect",
			name="code",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		wq_var = arcpy.Parameter(
			displayName="Water Quality Variable",
			name="wq_var",
			datatype="GPString",
			multiValue=True,
			direction="Input"
		)

		title = arcpy.Parameter(
			displayName="Title for graph",
			name="output",
			datatype="GPString",
			multiValue=False,
			direction="Input",
			parameterType="Optional"
		)

		output_folder = arcpy.Parameter(
			displayName="Output folder",
			name="output_folder",
			datatype="DEFolder",
			multiValue=False,
			direction="Input"
		)

		wq_var.filter.type = 'ValueList'
		wq_var.filter.list = ["temp","ph","sp_cond","salinity", "dissolved_oxygen","dissolved_oxygen_percent",
            "dep_25", "par", "rpar","turbidity_sc","chl", "chl_corrected", "m_value"]

		params = [code, wq_var, title, output_folder]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True


	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		# validate site name by pulling creating filter with names from table
		# get list of sites from the database profile sites table
		session = classes.get_new_session()
		try:
			sites = session.query(classes.Site).distinct().all()
			site_names = []

			# add profile name to site list
			for s in sites:
				combine = s.code + ' - ' + s.name
				site_names.append(combine)

			parameters[0].filter.type = 'ValueList'
			site_names.sort()
			parameters[0].filter.list = site_names

		finally:
			session.close()
		return


	@parameters_as_dict
	def execute(self, parameters, messages):

		sitecodename = parameters["code"].valueAsText
		sitecode = sitecodename.split(" - ")[0]

		wq_var_list = parameters["wq_var"].valueAsText.split(';')
		title_param = parameters["output"].valueAsText
		output_folder = parameters["output_folder"].valueAsText

		### DEFINE DATA PATHS ###
		base_path = config.arcwqpro
		gen_heat = os.path.join(base_path, "arcproject", "scripts", "generate_heatplots.R")

		R = launchR.Interpreter()

		for wq_var in wq_var_list:

			# set default title
			if title_param is None:
				title = sitecode.upper() + " - " + wq_var.upper()
			else:
				title = title_param
			try:
				R.run(gen_heat, "--args", sitecode, wq_var, title, output_folder)
			except launchR.RExecutionError as e:
				arcpy.AddWarning("Call to R failed - R gave the following output: {}".format(e.output))
				raise


class LinearRef(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Locate WQT Along Reference Route"
		self.description = "Locate water quality points using linear referencing to update " \
		                   "the m-value of selected records"
		self.canRunInBackground = False
		self.category = "Modify"

	def getParameterInfo(self):

		query = arcpy.Parameter(
			displayName="Type of query to select records to modify?",
			name="query",
			datatype="GPString",
			multiValue=False,
			direction="Input",
			parameterType="Required"
		)

		query.filter.type = "ValueList"
		query.filter.list = ["ALL", "DATERANGE", "IDRANGE"]


		over = arcpy.Parameter(
			displayName="Overwrite existing M Values?",
			name="over",
			datatype="GPBoolean",
			direction="Input",
			parameterType="Optional"
		)

		over.value = False

		date1 = arcpy.Parameter(
			displayName="Start date",
			name="date1",
			datatype="GPDate",
			direction="Input",
			parameterType="Optional"
		)

		date2 = arcpy.Parameter(
			displayName="End date",
			name="date2",
			datatype="GPDate",
			direction="Input",
			parameterType="Optional"
		)

		id1 = arcpy.Parameter(
			displayName="Start ID",
			name="id1",
			datatype="GPLong",
			direction="Input",
			parameterType="Optional"
		)

		id2 = arcpy.Parameter(
			displayName="End ID",
			name="id2",
			datatype="GPLong",
			direction="Input",
			parameterType="Optional"
		)


		params = [query, over, date1, date2, id1, id2]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		if parameters[0].valueAsText == "DATERANGE":
			parameters[2].enabled = True
			parameters[3].enabled = True
		else:
			parameters[2].enabled = False
			parameters[3].enabled = False

		if parameters[0].valueAsText == "IDRANGE":
			parameters[4].enabled = True
			parameters[5].enabled = True
		else:
			parameters[4].enabled = False
			parameters[5].enabled = False
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):

		query_type = parameters[0].valueAsText
		over = parameters[1].value

		start_date = parameters[2].value
		end_date = parameters[3].value

		start_id = parameters[4].value
		end_id = parameters[5].value

		arcpy.AddMessage("PARAMS: type = {}, overwrite = {}, start date = {}, "
		                 "end date = {}, start id = {}, end id = {}".format(query_type, over, start_date,
		                                                                    end_date, start_id, end_id))

		if start_date is not None and end_date is not None:

			# round python date time objects to start of the day (in case times are included in tbx input)
			start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
			end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

			date_range = [start_date, end_date]

		else:
			date_range = None

		if start_id is not None and end_id is not None:
			id_range = [start_id, end_id]
		else:
			id_range = None

		arcpy.AddMessage("Updating m values for wqt points. Be patient...")
		linear_ref.main(query_type, overwrite=over, dates=date_range, idrange=id_range)

		return


class GenerateSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Map Layer - One Transect (all days)"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Mapping"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		siteid = arcpy.Parameter(
			displayName="Transect",
			name="siteid",
			datatype="GPString",
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

		fc = mapping.set_output_symbology(fc)

		params = [siteid, fc, ]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		# validate site name by pulling creating filter with names from table
		# get list of sites from the database profile sites table
		session = classes.get_new_session()
		try:
			sites = session.query(classes.Site).distinct().all()
			site_names = []

			# add profile name to site list
			for s in sites:
				combine = s.code + ' - ' + s.name
				site_names.append(combine)

			parameters[0].filter.type = 'ValueList'
			site_names.sort()
			parameters[0].filter.list = site_names

		finally:
			session.close()
		return




		sitecodename = parameters["code"].valueAsText
		sitecode = sitecodename.split(" - ")[0]

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		arcpy.env.addOutputsToMap = True
		site_codename = parameters[0].valueAsText
		site_code = site_codename.split(" - ")[0]
		session = classes.get_new_session()
		siteid = swap_site_recs.lookup_siteid(session, site_code)
		session.close()

		output_location = parameters[1].valueAsText

		mapping.generate_layer_for_site(siteid, output_location)


class ModifySelectedSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Modify SiteID for Selected Records"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Modify"

	def getParameterInfo(self):
		"""Define parameter definitions"""
		site = arcpy.Parameter(
			displayName="New Site for Selected Features",
			name="siteid",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		wq = arcpy.Parameter(
			displayName="Water Quality Layer with Selection",
			name="shp_file",
			datatype="GPFeatureLayer",
			direction="Input"
		)

		params = [wq, site,]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		# validate site name by pulling creating filter with names from table
		# get list of sites from the database profile sites table
		session = classes.get_new_session()
		try:
			sites = session.query(classes.Site).distinct().all()
			site_names = []

			# add profile name to site list
			for s in sites:
				combine = s.code + ' - ' + s.name
				site_names.append(combine)

			parameters[1].filter.type = 'ValueList'
			site_names.sort()
			parameters[1].filter.list = site_names

		finally:
			session.close()

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		siteid_code = parameters[1].valueAsText
		site = siteid_code.split(" - ")[0]


		# selected features
		feature = parameters[0].value

		desc = arcpy.Describe(feature)

		if desc.FIDSet != '':
			num = len(desc.FIDSet.split(";"))
			arcpy.AddMessage("Updating {} records".format(num))
			ids_2_update = []
			with arcpy.da.SearchCursor(feature, ['id']) as cursor:
				for row in cursor:
					ids_2_update.append(int(row[0]))
			arcpy.AddMessage(ids_2_update)

			session = classes.get_new_session()

			siteid = swap_site_recs.lookup_siteid(session, site)

			try:
				for i in ids_2_update:
					wq = classes.WaterQuality
					q = session.query(wq).filter(wq.id == i).one()
					q.site_id = int(siteid)
				session.commit()
			finally:
				session.close()
		else:
			arcpy.AddMessage("No points selected. Make a selection first!")

		return


class DeleteMonth(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Delete Records for Month"
		self.description = "Deletes the water quality transects and gain files for a given month and year"
		self.canRunInBackground = False
		self.category = "Modify"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files

		year = arcpy.Parameter(
			displayName="Year",
			name="year",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		month = arcpy.Parameter(
			displayName="Month",
			name="monthe",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		month.filter.type = 'ValueList'
		t = list(calendar.month_name)
		t.pop(0)
		month.filter.list = t


		params = [year, month, ]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		# get years with data from the database to use as selection for tool input
		session = classes.get_new_session()
		try:
			q = session.query(extract('year', classes.WaterQuality.date_time)).distinct()

			print(q)
			years = []
			# add profile name to site list
			for year in q:
				print(year[0])
				years.append(year[0])
			parameters[0].filter.type = 'ValueList'
			parameters[0].filter.list = years

		finally:
			session.close()

		# get valid months for the selected year as the options for the tool input
		if parameters[0].value:
			Y = int(parameters[0].value)

			session = classes.get_new_session()
			try:

				q2 = session.query(extract('month', classes.WaterQuality.date_time)).filter(
					extract('year', classes.WaterQuality.date_time) == Y).distinct()
				months = []
				t = list(calendar.month_name)
				for month in q2:
					print(month[0])
					months.append(t[month[0]])

				print(months)
				parameters[1].filter.type = 'ValueList'
				parameters[1].filter.list = months
			finally:
				session.close()
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		year_to_use = int(parameters[0].value)
		month = parameters[1].value
		# look up index position in calender.monthname
		t = list(calendar.month_name)
		month_to_use = int(t.index(month))

		arcpy.AddMessage("YEAR: {}, MONTH: {}".format(year_to_use, month_to_use))

		arcpy.AddMessage("WARNING!: this will delete records. Quit now if you don't want to do this.")
		for i in range(10, 0, -1):
			time.sleep(1)
			arcpy.AddMessage(i)

		wq = classes.WaterQuality
		gn = classes.VerticalProfile
		session = classes.get_new_session()
		try:
			lower_bound = datetime.date(year_to_use, month_to_use, 1)
			upper_bound = datetime.date(year_to_use, month_to_use,
			                            int(calendar.monthrange(year_to_use, month_to_use)[1]))
			arcpy.AddMessage("Deleting data for {} through {}".format(lower_bound, upper_bound))
			q_wq = session.query(wq).filter(wq.date_time > lower_bound, wq.date_time < upper_bound)

			arcpy.AddMessage("Deleting transects")
			q_wq.delete()

			q_gn = session.query(gn).filter(gn.date_time > lower_bound, gn.date_time < upper_bound)

			arcpy.AddMessage("Deleting gains")
			q_gn.delete()

			# commit changes
			arcpy.AddMessage("WARNING!: final chance to not commit database change. Exit now!")
			for i in range(10, 0, -1):
				time.sleep(1)
				arcpy.AddMessage(i)
			arcpy.AddMessage("Changes committed. Records are deleted.")
			session.commit()

		finally:
			session.close()

		return


class RenameGrabs(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Rename grab + profiles for given date"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Regression"

	def getParameterInfo(self):
		"""Define parameter definitions"""


		date_to_generate = arcpy.Parameter(
			displayName="Date",
			name="date_to_generate",
			datatype="GPDate",
			multiValue=False,
			direction="Input"
		)

		wqp = arcpy.Parameter(
			displayName="",
			name="wqp",
			parameterType="GPValueTable",
			multiValue=True,
			direction="Input"
		)

		wqp.columns = [['GPString', 'Type'], ['GPString', 'Current'], ['GPString', 'New'], ['GPString', 'Notes'], ['GPString','ID']]

		params = [date_to_generate, wqp]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		if parameters[0].altered and parameters[1].values is None:
			d = parameters[0].value
			t = d + datetime.timedelta(days=1)  # add one day to get upper bound
			lower = d.date()
			upper = t.date()


			session = classes.get_new_session()
			try:
				vt = []  # blank value table

				# fills out the value table with the vertical profile info
				wqp_abs = session.query(classes.ProfileSite.abbreviation, classes.VerticalProfile.source) \
					.filter(classes.VerticalProfile.date_time.between(lower, upper)) \
					.filter(classes.ProfileSite.id == classes.VerticalProfile.profile_site_id) \
					.distinct().all()
				# cast(classes.VerticalProfile.date_time, Date) == date
				print(wqp_abs)

				for profile in wqp_abs:
					notes = "{}".format(profile[1])
					vt.append(['WQP', profile[0], profile[0], notes, "NA"])

				# fill out the grab sample info
				grab_abs = session.query(classes.GrabSample.profile_site_id, classes.GrabSample.lab_num,
				                         classes.GrabSample.sample_id,
				                         classes.GrabSample.site_id, classes.GrabSample.source, classes.GrabSample.id) \
					.filter(classes.GrabSample.date.between(lower, upper)) \
					.distinct().all()

				for profile in grab_abs:
					notes = "{}, {}, {}, {}".format(profile[1], profile[2], profile[3], profile[4])

					# some of the grab samples don't have profile_site and should return None
					pro_abbrev = swap_site_recs.lookup_profile_abbreviation(session, profile[0])

					vt.append(["GRAB", pro_abbrev, pro_abbrev, notes, profile[5]])

				sorted_vt = sorted(vt, key = lambda x: x[1])
				parameters[1].values = sorted_vt

				# potential profile abbreviations
				profiles = session.query(classes.ProfileSite.abbreviation).distinct().all()
				profile_abbreviation = []

				# add profile name to site list
				for profile in profiles:
					profile_abbreviation.append(profile[0])

				parameters[1].filters[2].type = 'ValueList'
				parameters[1].filters[2].list = profile_abbreviation

			finally:
				session.close()

		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	@parameters_as_dict
	def execute(self, parameters, messages):

		d = parameters["date_to_generate"].value
		t = d + datetime.timedelta(days=1)  # add one day to get upper bound
		lower = d.date()
		upper = t.date()

		# get the vt parameters
		vt = parameters["wqp"].values  # values are list of lists

		for i in range(0, len(vt)):

			record_type = vt[i][0]
			current = vt[i][1]
			new = vt[i][2]
			grabid = vt[i][4]

			if current == new:
				pass

			elif record_type == "WQP":
				arcpy.AddMessage("Changing {} to {} for {} records on {}".format(current, new, record_type, lower))

				session = classes.get_new_session()
				try:
					query = session.query(classes.VerticalProfile) \
						.filter(classes.VerticalProfile.date_time.between(lower, upper)) \
						.filter(classes.ProfileSite.id == classes.VerticalProfile.profile_site_id) \
						.filter(classes.ProfileSite.abbreviation == current).all()

					for q in query:
						q.profile_site_id = swap_site_recs.lookup_profile_site_id(session, new)

					session.commit()

				finally:
					session.close()

			elif record_type == "GRAB":
				arcpy.AddMessage("Changing {} to {} for {} records on {}".format(current, new, record_type, lower))

				session = classes.get_new_session()
				try:
					query = session.query(classes.GrabSample) \
						.filter(classes.GrabSample.date.between(lower, upper)) \
						.filter(classes.GrabSample.id == grabid).one()

					query.profile_site_id = swap_site_recs.lookup_profile_site_id(session, new)

					session.commit()

				finally:
					session.close()

		return


class RegressionPlot(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Regression Plot"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Regression"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		date_to_generate = arcpy.Parameter(
			displayName="Date",
			name="date_to_generate",
			datatype="GPDate",
			multiValue=False,
			direction="Input")

		gain_setting = arcpy.Parameter(
			displayName="Gain Setting",
			name="gain_setting",
			datatype="GPString",
			multiValue=False,
			direction="Input")

		#gain_setting.filter.type = 'ValueList'
		#gain_setting.filter.list = ['0', '1', '10', '100']

		depths = arcpy.Parameter(
			displayName="All depths?",
			name="depths",
			datatype="GPBoolean",
			parameterType="Optional")

		preview = arcpy.Parameter(
			displayName="Preview?",
			name="preview",
			datatype="GPBoolean",
			parameterType="Optional")

		output = arcpy.Parameter(
			displayName="Output Location for Graph",
			name="output",
			datatype="DEFile",
			parameterType="Optional",
			direction="Output")

		commit = arcpy.Parameter(
			displayName="Commit regression to the database?",
			name="commit",
			datatype="GPBoolean",
			parameterType="Optional")

		params = [date_to_generate, gain_setting, depths, preview, output, commit]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		if parameters[0].altered:
			# turn off params (clicking box when tool is running with crash arc)
			parameters[1].enabled = True

			d = parameters[0].value
			t = d + datetime.timedelta(days=1)  # add one day to get upper bound
			lower = d.date()
			upper = t.date()

			session = classes.get_new_session()
			try:

				gains = session.query(classes.VerticalProfile.gain_setting) \
					.filter(classes.VerticalProfile.date_time.between(lower, upper)) \
					.distinct().all()

				gain_settings = []

				# add profile name to site list
				for g in gains:
					print(g[0])
					gain_settings.append(g[0])

				parameters[1].filter.type = 'ValueList'
				parameters[1].filter.list = gain_settings

			finally:
				session.close()

		else:
			parameters[1].enabled = False


		if parameters[0].value and parameters[1].altered:
			# turn off params (clicking box when tool is running with crash arc)
			parameters[2].enabled = True
			parameters[3].enabled = True
		else:
			parameters[2].enabled = False
			parameters[3].enabled = False

		if parameters[3].value is True: # add in conditional for other two params

			### DEFINE DATA PATHS ###
			base_path = config.arcwqpro
			rscript_path = config.rscript  # path to R exe
			chl_reg = os.path.join(base_path, "arcproject", "scripts", "chl_regression.R")

			date_time = parameters[0].value
			date = str(date_time.date())
			gain = parameters[1].valueAstext
			output = os.path.join(base_path, "arcproject", "plots", "chl_regression_tool_preview.png")

			if parameters[2].value:
				depths = "TRUE"
			else:
				depths = "FALSE"

			try:
				CREATE_NO_WINDOW = 0x08000000  # used to hide the console window so it stays in the background
				subprocess.check_output([rscript_path, chl_reg, "--args", date, gain, output, depths, "FALSE"],
				                        creationflags=CREATE_NO_WINDOW,
				                        stderr=subprocess.STDOUT)  # ampersand makes it run without a console window
				webbrowser.open(output)

			except subprocess.CalledProcessError as e:
				arcpy.AddError("Call to R returned exit code {}.\nR output the following while processing:\n{}".format(
					e.returncode, e.output))
			finally:
				parameters[3].value = False
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):

		### DEFINE DATA PATHS ###
		base_path = config.arcwqpro
		rscript_path = config.rscript  # path to R exe
		chl_reg = os.path.join(base_path, "arcproject", "scripts", "chl_regression.R")
		date_time = parameters[0].value
		date = str(date_time.date())
		gain = parameters[1].valueAstext
		output = parameters[4].valueAstext

		if parameters[2].value:
			depths = "TRUE"
		else:
			depths = "FALSE"


		if parameters[5].value:
			commit = "TRUE"
		else:
			commit = "FALSE"

		if output is None:
			output = os.path.join(base_path, "arcproject", "plots", "chl_regression_tool_preview.png")

		arcpy.AddMessage("{}, {}, {}, {}, {}, {}, {},{}".format(rscript_path, chl_reg, "--args", date, gain, output, depths, commit))

		try:
			CREATE_NO_WINDOW = 0x08000000  # used to hide the console window so it stays in the background
			subprocess.check_output([rscript_path, chl_reg, "--args", date, gain, output, depths, commit],
			                        creationflags=CREATE_NO_WINDOW,
			                        stderr=subprocess.STDOUT)  # ampersand makes it run without a console window

		except subprocess.CalledProcessError as e:
			arcpy.AddError("Call to R returned exit code {}.\nR output the following while processing:\n{}".format(
				e.returncode, e.output))

		return


class CorrectChl(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Correct Chl Values"
		self.description = "Correct Chl values from regression table."
		self.canRunInBackground = False
		self.category = "Regression"

	def getParameterInfo(self):

		query = arcpy.Parameter(
			displayName="Type of query to select records to modify?",
			name="query",
			datatype="GPString",
			multiValue=False,
			direction="Input",
			parameterType="Required"
		)

		query.filter.type = "ValueList"
		query.filter.list = ["ALL", "NEW", "DATERANGE", "IDRANGE"]

		date1 = arcpy.Parameter(
			displayName="Start date",
			name="date1",
			datatype="GPDate",
			direction="Input",
			parameterType="Optional"
		)

		date2 = arcpy.Parameter(
			displayName="End date",
			name="date2",
			datatype="GPDate",
			direction="Input",
			parameterType="Optional"
		)

		id1 = arcpy.Parameter(
			displayName="Start ID",
			name="id1",
			datatype="GPLong",
			direction="Input",
			parameterType="Optional"
		)

		id2 = arcpy.Parameter(
			displayName="End ID",
			name="id2",
			datatype="GPLong",
			direction="Input",
			parameterType="Optional"
		)


		params = [query, date1, date2, id1, id2]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True

	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		if parameters[0].valueAsText == "DATERANGE":
			parameters[1].enabled = True
			parameters[2].enabled = True
		else:
			parameters[1].enabled = False
			parameters[2].enabled = False

		if parameters[0].valueAsText == "IDRANGE":
			parameters[3].enabled = True
			parameters[4].enabled = True
		else:
			parameters[3].enabled = False
			parameters[4].enabled = False
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):

		query_type = parameters[0].valueAsText

		start_date = parameters[1].value
		end_date = parameters[2].value

		start_id = parameters[3].value
		end_id = parameters[4].value

		arcpy.AddMessage("PARAMS: type = {}, start date = {}, "
		                 "end date = {}, start id = {}, end id = {}".format(query_type, start_date,
		                                                                    end_date, start_id, end_id))

		if start_date is not None and end_date is not None:

			# round python date time objects to start of the day (in case times are included in tbx input)
			start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
			end_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)

			date_range = [start_date, end_date]

		else:
			date_range = None

		if start_id is not None and end_id is not None:
			id_range = [start_id, end_id]
		else:
			id_range = None

		arcpy.AddMessage("Updating Chl values for points. Be patient...")
		chl_decision_tree.main(query_type, daterange=date_range, idrange=id_range)

		return


class ExportHeatPlotData(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Export Heatplot data CSV"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Mapping"

	def getParameterInfo(self):

		code = arcpy.Parameter(
			displayName="Code for Transect",
			name="code",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)


		output_csv = arcpy.Parameter(
			displayName="Output CSV",
			name="output_csv",
			datatype="DEFile",
			multiValue=False,
			direction="Output"
		)

		params = [code, output_csv]
		return params

	def isLicensed(self):
		"""Set whether tool is licensed to execute."""
		return True


	def updateParameters(self, parameters):
		"""Modify the values and properties of parameters before internal
		validation is performed.  This method is called whenever a parameter
		has been changed."""

		# validate site name by pulling creating filter with names from table
		# get list of sites from the database profile sites table
		session = classes.get_new_session()
		try:
			sites = session.query(classes.Site).distinct().all()
			site_names = []

			# add profile name to site list
			for s in sites:
				combine = s.code + ' - ' + s.name
				site_names.append(combine)

			parameters[0].filter.type = 'ValueList'
			site_names.sort()
			parameters[0].filter.list = site_names

		finally:
			session.close()
		return


	@parameters_as_dict
	def execute(self, parameters, messages):

		sitecodename = parameters["code"].valueAsText
		sitecode = sitecodename.split(" - ")[0]

		output_file = parameters["output_csv"].valueAsText

		arcpy.AddMessage("Saving WaterQuality for site {} as csv.\n{}".format(sitecodename, output_file))

		try:
			outfile = open(output_file, 'wb')
			outcsv = csv.writer(outfile)

			session = classes.get_new_session()
			records = session.query(classes.WaterQuality).filter(classes.Site.code == sitecode).\
				filter(classes.Site.id == classes.WaterQuality.site_id)
			outcsv.writerow([column.name for column in classes.WaterQuality.__mapper__.columns])  # header as row 1
			[outcsv.writerow([getattr(curr, column.name) for column in classes.WaterQuality.__mapper__.columns]) for
			 curr in records]

			outfile.close()
		finally:
			session.close()
		return