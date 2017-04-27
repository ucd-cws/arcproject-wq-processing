import calendar
import datetime
import os
import logging

log = logging.getLogger("arcproject")

import arcpy
from sqlalchemy import extract
import pandas as pd

import amaptor

from arcproject.waterquality.classes import get_new_session, WaterQuality
from .exceptions import NoRecordsError, SpatialReferenceError
from .wqt_timestamp_match import pd2np
from arcproject.waterquality import classes
from arcproject.scripts import funcs as wq_funcs

_BASE_FOLDER = os.path.split(os.path.dirname(__file__))[0]
_TEMPLATES_FOLDER = os.path.join(_BASE_FOLDER, "templates", )
_LAYERS_FOLDER = os.path.join(_TEMPLATES_FOLDER, "layers")

arcgis_10_template = os.path.join(_TEMPLATES_FOLDER, "base_template.mxd")
arcgis_pro_template = os.path.join(_TEMPLATES_FOLDER, "arcproject_template_pro", "arcproject_template_pro.aprx")
arcgis_pro_layout_template = os.path.join(_TEMPLATES_FOLDER, "arcproject_template_pro", "main_layout.pagx")

arcgis_pro_layer_symbology = os.path.join(_LAYERS_FOLDER, "wq_points.lyrx")
arcgis_10_layer_symbology = os.path.join(_LAYERS_FOLDER, "wq_points.lyr")

def set_output_symbology(parameter):
	## Output symbology
	if arcpy.GetInstallInfo()["ProductName"] == "ArcGISPro":
		parameter.symbology = arcgis_pro_layer_symbology
	else:
		parameter.symbology = arcgis_10_layer_symbology

	return parameter


def layer_from_date(date_to_use, output_location):
	"""
		Given a date and output location, exports records to a feature class
	:param date_to_use: date in MM/DD/YYYY format or a datetime object
	:param output_location: full path to output feature class
	:return: returns nothing
	"""

	wq = classes.WaterQuality
	session = classes.get_new_session()

	try:
		arcpy.AddMessage("Using Date {}".format(date_to_use))
		upper_bound = date_to_use.date() + datetime.timedelta(days=1)
		query = session.query(wq).filter(wq.date_time > date_to_use.date(), wq.date_time < upper_bound, wq.x_coord != None, wq.y_coord != None)  # add 1 day's worth of nanoseconds

		try:
			query_to_features(query, output_location)
		except NoRecordsError:
			arcpy.AddWarning("No records for date {}".format(date_to_use))
			raise
	finally:
		session.close()


def generate_layer_for_month(month_to_use, year_to_use, output_location):
	wq = classes.WaterQuality
	session = classes.get_new_session()
	try:
		lower_bound = datetime.date(year_to_use, month_to_use, 1)
		upper_bound = datetime.date(year_to_use, month_to_use, int(calendar.monthrange(year_to_use, month_to_use)[1]))
		arcpy.AddMessage("Pulling data for {} through {}".format(lower_bound, upper_bound))
		query = session.query(wq).filter(wq.date_time > lower_bound, wq.date_time < upper_bound, wq.x_coord != None, wq.y_coord != None)  # add 1 day's worth of nanoseconds
		query_to_features(query, output_location)
	finally:
		session.close()


def generate_layer_for_site(siteid, output_location):
	wq = classes.WaterQuality
	session = classes.get_new_session()
	try:
		query = session.query(wq).filter(wq.site_id == siteid, wq.x_coord != None, wq.y_coord != None)
		query_to_features(query, output_location)
	finally:
		session.close()


def replaceDefaultNull(fc, placeholder=-9999):
	if fc.endswith(".shp"):  # skip shapefiles because they don't support null
		return

	try:
		with arcpy.da.UpdateCursor(fc, '*') as cursor:
			for row in cursor:
				for i in range(len(row)):
					if row[i] == placeholder or row[i] == str(placeholder):
						row[i] = None

				cursor.updateRow(row)
	except Exception as e:
		print(e.message)


def query_to_features(query, export_path):
	"""
	Given a SQLAlchemy query for water quality data, exports it to a feature class
	:param query: a SQLAlchemy query object
	:param export_path: the path to write out a feature class to
	:return:
	"""

	# read the SQLAlchemy query into a Pandas Data Frame since that can talk to ArcGIS
	df = pd.read_sql(query.statement, query.session.bind)

	# confirm that all of the items are in the same spatial reference - this should always be the case, but we should
	# make sure so nothing weird happens

	sr_code = wq_funcs.get_wq_df_spatial_reference(df)

	sr = arcpy.SpatialReference(int(sr_code))  # make a spatial reference object

	arcpy.da.NumPyArrayToFeatureClass(
		in_array=pd2np(df),
		out_table=export_path,
		shape_fields=["x_coord", "y_coord"],
		spatial_reference=sr,
	)

	# replace -9999 with <null> for geodatabase. Shapefile no data will remain -9999
	replaceDefaultNull(export_path)


def map_missing_segments(summary_file, loaded_data, output_location, template=os.path.join(_TEMPLATES_FOLDER, "base_template.mxd")):
	"""
		A mapping function used by data validation code to create maps when data is invalid
	:param summary_file:
	:param loaded_data:
	:param output_location:
	:param template:
	:return:
	"""

	transect_template = os.path.join(_LAYERS_FOLDER, "added_data.lyr")
	summary_file_template = os.path.join(_LAYERS_FOLDER, "summary_file_review.lyr")

	project = amaptor.Project(template)
	map = project.maps[0]
	map.insert_feature_class_with_symbology(summary_file, layer_file=summary_file_template, layer_name="Summary File",
											near_name="Arc_DeltaWaterways_0402", insert_position="BEFORE")
	map.insert_feature_class_with_symbology(loaded_data, layer_file=transect_template, layer_name="Loaded Transects",
											near_name="Arc_DeltaWaterways_0402", insert_position="BEFORE")

	project.save_a_copy(output_location)

	return project


class WQMappingBase(object):
	"""
		A base class for tools that want to provide a choice for how to symbolize water quality data. To use, subclass it
		for any of the other tools, add the defined parameter to the list of params,
		 and make sure the tool init includes a call to super(NewClassName, self).__init__() at the beginning of __init__
	"""
	def __init__(self):
		self.table_workspace = "in_memory"
		self.table_name = "arcproject_temp_date_table"
		self.temporary_date_table = "{}\\{}".format(self.table_workspace, self.table_name)

		self.select_wq_param = arcpy.Parameter(
			displayName="Symbolize Data by",
			name="symbology",
			datatype="GPString",
			multiValue=False,
			direction="Input",
		)

		self.year_to_generate = arcpy.Parameter(  # optional to use, but available
			displayName="Year",
			name="year_to_generate",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		self.month_to_generate = arcpy.Parameter(  # optional to use, but available
			displayName="Month",
			name="month_to_generate",
			datatype="GPString",
			multiValue=False,
			direction="Input"
		)

		self.month_to_generate.filter.type = 'ValueList'
		t = list(calendar.month_name)
		t.pop(0)
		self.month_to_generate.filter.list = t


		self._filter_to_layer_mapping = {
										"CHL": "CHL_regular.lyr",
										"CHL Corrected": "CHL_corrected.lyr",
										"Dissolved Oxygen": "DO_v2.lyr",
										"DO Percent Saturation": "DOPerCentSat_v2.lyr",
										"pH": "pH.lyr",
										"RPAR": "RPAR_v2.lyr",
										"Salinity": "Sal.lyr",
										"SpCond": "SpCond.lyr",
										"Temperature": "Temp.lyr",
										"Turbidity": "Turbid.lyr",
									}

		self.select_wq_param.filter.type = "ValueList"
		self.select_wq_param.filter.list = ["CHL", "Corrected CHL", "Dissolved Oxygen", "DO Percent Saturation", "pH", "RPAR", "Salinity", "SpCond",
							"Temperature", "Turbidity"]


	def insert_layer(self, data_path, symbology_param, map_or_project="CURRENT"):
		"""
			Symbolizes a WQ layer based on the specified parameter and then inserts it into a map
		:param data_path:
		:param symbology_param:
		:param map_or_project: a reference to a map document (including "CURRENT"), an instance of amaptor.Project, or
			and instance of amaptor.Map
		:return:
		"""

		if isinstance(map_or_project, amaptor.Project):
			project = map_or_project
			l_map = project.get_active_map()
		elif isinstance(map_or_project, amaptor.Map):
			l_map = map_or_project
		else:
			project = amaptor.Project(map_or_project)
			l_map = project.get_active_map()

		layer_name = self._filter_to_layer_mapping[symbology_param.valueAsText]
		layer_path = os.path.join(_LAYERS_FOLDER, layer_name)

		layer = amaptor.functions.make_layer_with_file_symbology(data_path, layer_path)
		layer.name = os.path.split(data_path)[1]
		l_map.add_layer(layer)

	def cleanup(self):
		if arcpy.Exists(self.temporary_date_table):
			arcpy.Delete_management(self.temporary_date_table)

	def update_month_fields(self, parameters, year_field_index=0, month_field_index=1):
		"""
			Retrieve months from the temporary data table in memory
		:param parameters:
		:param year_field_index:
		:param month_field_index:
		:return:
		"""

		if parameters[year_field_index].filter.list is None or parameters[year_field_index].filter.list == "" or len(parameters[year_field_index].filter.list) == 0:  # if this is our first time through, set it all up
			self.initialize_year_and_month_fields(parameters, year_field_index)

		if not arcpy.Exists(self.temporary_date_table):
			return  # this seems to occur in Pro, when running the tool - the data doesn't get loaded, but it is calling this function - may be a bug to squash somewhere here.

		year = int(parameters[year_field_index].value)
		months = arcpy.SearchCursor(self.temporary_date_table, where_clause="data_year={}".format(year))

		filter_months = []
		for month in months:
			filter_months.append(month.getValue("data_month"))

		parameters[month_field_index].filter.type = 'ValueList'
		parameters[month_field_index].filter.list = filter_months

	def initialize_year_and_month_fields(self, parameters, year_field_index=0):
		"""
			Used on Generate Month and Generate Map
		:param parameters:
		:return:
		"""

		self.cleanup()  # cleans up the temporary table. If it exists, it's stale

		arcpy.CreateTable_management(self.table_workspace, self.table_name)
		arcpy.AddField_management(self.temporary_date_table, "data_year", "LONG")
		arcpy.AddField_management(self.temporary_date_table, "data_month", "TEXT")

		# load the data from the DB
		session = get_new_session()

		try:
			# get years with data from the database to use as selection for tool input

			curs = arcpy.InsertCursor(self.temporary_date_table)
			q = session.query(extract('year', WaterQuality.date_time), extract('month', WaterQuality.date_time)).distinct()
			years = {}
			month_names = list(calendar.month_name)  # helps translate numeric months to
			for row in q:  # translate the results to the temporary table
				new_record = curs.newRow()
				new_record.setValue("data_year", row[0])
				new_record.setValue("data_month", month_names[row[1]])
				curs.insertRow(new_record)

				years[row[0]] = True  # indicate we have data for a year

			parameters[year_field_index].filter.type = 'ValueList'
			parameters[year_field_index].filter.list = sorted(list(years.keys()))  # get the distinct set of years

		finally:
			session.close()

		return self.temporary_date_table

	def convert_year_and_month(self, year, month):
		year_to_use = int(year.value)
		month = month.valueAsText
		# look up index position in calender.monthname
		t = list(calendar.month_name)
		month_to_use = int(t.index(month))
		return year_to_use, month_to_use