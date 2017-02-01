import calendar
import os
import subprocess
from string import digits
import datetime
import arcpy
from sqlalchemy import exc, func, distinct, extract
import time
from scripts import mapping
from scripts import wq_gain
from scripts import wqt_timestamp_match
from scripts.mapping import generate_layer_for_month
from scripts import swap_site_recs
from scripts import linear_ref

from waterquality import classes


class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
		self.label = "ArcProject WQ Toolbox"
		self.alias = "ArcProject WQ Toolbox"
		# List of tool classes associated with this toolbox
		self.tools = [AddSite, AddGainSite, JoinTimestamp, CheckMatch,
		              GenerateWQLayer, GainToDB, GenerateMonth, ModifyWQSite, GenerateHeatPlot,
		              GenerateSite, ModifySelectedSite, DeleteMonth]


class AddSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "New Site (slough)"
		self.description = "Add a new site to the database. Each slough should have it's own unique site id."
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
		self.description = "Create a new vertical profile site to add to the database"
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
			displayName="Slough?",
			name="slough",
			datatype="GPString",
			multiValue=False,
			direction="Input"
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

	def execute(self, parameters, messages):

		abbr = parameters[0].valueAsText
		slough = parameters[1].valueAsText
		ps = classes.ProfileSite()
		ps.abbreviation = abbr.upper()
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


class GenerateWQLayer(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Generate Map Layer from Water Quality Data"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Mapping"

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

		mapping.layer_from_date(date_to_use, output_location)


class JoinTimestamp(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Transect - Join on Timestamp"
		self.description = "Join water quality transect to gps using time stamp and add to database"
		self.canRunInBackground = False
		self.category = "Add Data"

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


class CheckMatch(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Percent Match - Water Quality data with Transect"
		self.description = "Reports the percent match for multiple water quality dataset with transect shapefile"
		self.canRunInBackground = False
		self.category = "Add Data"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files
		wqt = arcpy.Parameter(
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
			datatype="DEFeatureClass",
			direction="Input"
		)

		add = arcpy.Parameter(
			displayName="Add to database?",
			name="add",
			datatype="GPBoolean",
			direction="Input"
		)

		params = [wqt, bc, add]
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
		wq_transect_list = parameters[0].valueAsText

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
		self.description = ""
		self.canRunInBackground = False
		self.category = "Add Data"

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
			datatype="GPBoolean",
			parameterType="Optional"
		)

		site_part = arcpy.Parameter(
			displayName="Part of filename with site code (split by underscores)?",
			name="site",
			datatype="GPLong",
			parameterType="Optional"
		)

		site_part.value = 3
		site_part.filter.type = "ValueList"
		site_part.filter.list = [1, 2, 3, 4, 5, 6]


		gain_part = arcpy.Parameter(
			displayName="Part of filename with gain code (split by underscores)?",
			name="gain",
			datatype="GPLong",
			parameterType="Optional"
		)

		gain_part.value = 5
		gain_part.filter.type = "ValueList"
		gain_part.filter.list = [1, 2, 3, 4, 5, 6]

		params = [wqp, bool, site_part, gain_part]
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
				site = parts[int(parameters[2].value)-1]
				gain = parts[int(parameters[3].value)-1]
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


class GenerateMonth(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "All WQ Transects for Single Month"
		self.description = "Generate a layer of all the water quality transects for a given month and year"
		self.canRunInBackground = False
		self.category = "Mapping"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files

		year_to_generate = arcpy.Parameter(
			displayName="Year",
			name="year_to_generate",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		month_to_generate = arcpy.Parameter(
			displayName="Month",
			name="month_to_generate",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		month_to_generate.filter.type = 'ValueList'
		t = list(calendar.month_name)
		t.pop(0)
		month_to_generate.filter.list = t

		# shapefile for the transects GPS breadcrumbs
		fc = arcpy.Parameter(
			displayName="Output Feature Class",
			name="output_feature_class",
			datatype="DEFeatureClass",
			direction="Output"
		)

		fc = mapping.set_output_symbology(fc)

		params = [year_to_generate, month_to_generate, fc, ]
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

		output_location = parameters[2].valueAsText

		generate_layer_for_month(month_to_use, year_to_use, output_location)

    
class ModifyWQSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Modify assigned site for WQ records"
		self.description = ""
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
			multiValue=False,
			direction="Input"
		)

		title = arcpy.Parameter(
			displayName="Title for graph",
			name="output",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		wq_var.filter.type = 'ValueList'
		wq_var.filter.list = ["temp","ph","sp_cond","salinity", "dissolved_oxygen","dissolved_oxygen_percent",
            "dep_25", "par", "rpar","turbidity_sc","chl", "chl_volts","chl_corrected","corrected_gain"]

		params = [code, wq_var, title]
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

		finally:
			session.close()
		return

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):

		sitecode = parameters[0].valueAsText
		wq_var = parameters[1].valueAsText
		title = parameters[2].valueAsText


		### DEFINE DATA PATHS ###
		base_path = os.path.split(os.path.abspath(__file__))[0]

		# path to R exe
		rscript_path = r"C:\Program Files\R\R-3.2.3\bin\rscript.exe" # TODO update this depending on r install local
		gen_heat = os.path.join(base_path, "scripts", "generate_heatplots.R")
		arcpy.AddMessage("{}".format([rscript_path, gen_heat, "--args", sitecode, wq_var, title]))
		subprocess.call([rscript_path, gen_heat, "--args", sitecode, wq_var, title])
		return


class LinearRef(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Locate along reference line"
		self.description = "Locate water quality points along a reference line"
		self.canRunInBackground = False
		self.category = "Modify"

	def getParameterInfo(self):

		query = arcpy.Parameter(
			displayName="Query for records to modify",
			name="query",
			datatype="GPString",
			multiValue=False,
			direction="Input",
			parameterType="Optional"
		)

		query.filter.type = "ValueList"
		query.filter.list = ["All", "Last Month"]

		ref = arcpy.Parameter(
			displayName="Reference Line",
			name="ref",
			datatype="GP",
			multiValue=False,
			direction="Input",
			parameterType="Optional"
		)

		over = arcpy.Parameter(
			displayName="Override existing M Values?",
			name="over",
			datatype="GPBoolean",
			direction="Input",
			parameterType="Optional"
		)

		params = [query, ref, over]
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

		query = parameters[0].valueAsText
		ref_line = parameters[1].valueAsText
		over = parameters[2].valueAsText

		session = classes.get_new_session()

		if query == "All" and over is False:
			q = session.query(classes.WaterQuality).filter(classes.WaterQuality.m_value == None,
			                                           classes.WaterQuality.y_coord != None,
			                                           classes.WaterQuality.x_coord != None).all()
		elif query == "All" and over is True:
			q = session.query(classes.WaterQuality).filter(classes.WaterQuality.y_coord != None,
			                                               classes.WaterQuality.x_coord != None).all()
		elif query == "Last Month":
			q = "test"



		linear_ref.main(session, query, ref_line)

		return


class GenerateSite(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "SiteID- All WQ Transects"
		self.description = ""
		self.canRunInBackground = False
		self.category = "Mapping"

	def getParameterInfo(self):
		"""Define parameter definitions"""

		# parameter info for selecting multiple csv water quality files

		siteid = arcpy.Parameter(
			displayName="SiteID",
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
				combine = str(s.id) + ' - ' + s.code
				site_names.append(combine)

			parameters[0].filter.type = 'ValueList'
			parameters[0].filter.list = site_names

		finally:
			session.close()

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		siteid_code = parameters[0].valueAsText
		siteid = int(siteid_code.split(" - ")[0])

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

		# parameter info for selecting multiple csv water quality files

		siteid = arcpy.Parameter(
			displayName="New SiteID",
			name="siteid",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		wq =  arcpy.Parameter(
			displayName="WQ points to change site code",
			name="shp_file",
			datatype="GPFeatureLayer",
			direction="Input"
		)

		params = [siteid, wq]
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
				combine = str(s.id) + ' - ' + s.code
				site_names.append(combine)

			parameters[0].filter.type = 'ValueList'
			parameters[0].filter.list = site_names

		finally:
			session.close()

	def updateMessages(self, parameters):
		"""Modify the messages created by internal validation for each tool
		parameter.  This method is called after internal validation."""
		return

	def execute(self, parameters, messages):
		"""The source code of the tool."""
		siteid_code = parameters[0].valueAsText
		siteid = int(siteid_code.split(" - ")[0])

		# selected features
		feature = parameters[1].value

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

			try:
				for i in ids_2_update:
					wq = classes.WaterQuality
					q = session.query(wq).filter(wq.id == i).one()
					q.site_id = siteid
				session.commit()
			finally:
				session.close()
		else:
			arcpy.AddMessage("No points selected. Make a selection first!")

		return



class DeleteMonth(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Deletes records for month"
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
			arcpy.AddMessage("Changes commit. Records are deleted.")
			session.commit()

		finally:
			session.close()

		return
