import logging
import traceback
import six
from string import digits
import os

import pandas as pd

from arcproject.waterquality import classes
from . import wqt_timestamp_match as wqt


def convert_wq_dtypes(df):  # TODO check to see if the wq_from_file function can do this
	"""
	Converts all the strings in dataframe into numeric (pd.to_numeric introduced in 0.17 so can't use that)
	:param df:
	:return: dataframe with columns converted to numeric
	"""
	for column in list(df.columns.values):
		if df[column].dtype == object:
			if pd.__version__ >= "0.17":  # separate ways to convert to numeric before and after version 0.17
				try:
					df[column] = pd.to_numeric(df[column])
				except ValueError:  # try coercing the numeric fields - if it an exception is raised, we should be able to continue becuase we just need to numbers to act like numbers - it's ok if text stays text
					pass
			else:
				df[column] = df[column].convert_objects(convert_numeric=True)
	return df


def profile_function_historic(*args, **kwargs):
	"""
	Site functions are passed to wq_df2database so that it can determine which site a record is from. Historic data
	will use this function since it will parse if off the data frame as constructed in this code (which includes
	a field for the filename, which has the site code). Future data will have another method and use a different site
	function that will be passed to wq_df2database

	:param args:
	:param kwargs:
	:return: site object
	"""
	part = kwargs["part"]
	filename = kwargs["filename"]  # get the value of the data source field (source_field defined globally)
	try:
		filename = os.path.splitext(filename)[0]
		part_code = filename.split("_")[int(part)].upper()  # get the selected underscored part of the name
	except IndexError:
		raise IndexError("Filename was unable to be split based on underscore in order to parse site name -"
		                 " be sure your filename format matches the site function used, or that you're using "
		                 "the correct site retrieval function")
	return part_code


def gain_wq_df2database(data, field_map=classes.gain_water_quality_header_map, session=None):
	"""
	Given a pandas data frame of water quality records, translates those records to ORM-mapped objects in the database.

	:param data: a pandas data frame of water quality records
	:param field_map: a field map (dictionary) that translates keys in the data frame (as the dict keys) to the keys used
		in the ORM - uses a default, but when the schema of the data files is different, a new field map will be necessary
	:param session: a SQLAlchemy session to use - for tests, we often want the session passed so it can be inspected,
		otherwise, we'll likely just create it. If a session is passed, this function will NOT commit new records - that
		becomes the responsibility of the caller.
	:return:
	"""

	if not session:  # if no session was passed, create our own
		session = classes.get_new_session()
		session_created = True
	else:
		session_created = False

	try:
		records = data.iterrows()
		for row in records:  # iterates over all of the rows in the data frames the fast way
			gain_make_record(field_map, row[1], session)  # row[1] is the actual data included in the row
		if session_created:  # only commit if this function created the session - otherwise leave it to caller
			session.commit()  # saves all new objects
	finally:
		if session_created:
			session.close()


def gain_make_record(field_map, row, session):
	"""
	Called for each record in the loaded and joined Pandas data frame. Given a named tuple of a row in the data frame,
	 translates it into a profile object
	:param field_map: A field map dictionary with keys based on the data frame fields and values of the database field
	:param row: a named tuple of the row in the data frame to translate into the profile object
	:param session: an open SQLAlchemy database session
	:return:
	"""

	profile = classes.VerticalProfile()  # instantiates a new object

	for key in row.index:  # converts named_tuple to a Dict-like and gets the keys
		# look up the field that is used in the ORM/database using the key from the namedtuple.
		try:
			class_field = field_map[key]
		except KeyError:
			# logging.warning("Skipping field {} with value {}. Field not found in field map.".format(key, getattr(row, key)))
			continue

		if class_field is None:  # if it's an explicitly defined None and not nonexistent, then skip it silently
			continue

		try:
			setattr(profile, class_field, getattr(row, key))  # for each value, it sets the object's value to match
		except AttributeError:
			print("Incorrect field map - original message was {}".format(traceback.format_exc()))

	else:  # if we don't break for a bad site code or something else, then add the object
		session.add(profile)  # adds the object for creation in the DB - will be committed later.
	return


def profile_from_text(session, profile_abbreviation):
	"""
		Given a site code and an open database session, returns the site object
	:param session: An open database session
	:param profile_abbreviation: a text string that matches a code in the database
	:return: ProfileSite object
	"""
	return session.query(classes.ProfileSite).filter(classes.ProfileSite.abbreviation == profile_abbreviation).one()


def main(gain_file, site=profile_function_historic, gain=profile_function_historic, site_gain_params=wqt.site_function_params):
	"""
	Takes a water quality vertical profile at a specific site, date, and gain setting and adds to database
	:param gain_file: vertical gain profile
	:param site: a unique identifier for the site (2-4 letter character string) or a function to parse the profile name
	:param gain: the gain setting used when recording the water quality data ("0", "1", "10", "100") or a function to
	parse the gain setting
	:param site_gain_params: parameters to pass to the site function
	:return:
	"""

	# convert raw water quality gain file into pandas dataframe using function from wqt_timestamp_match
	gain_df = wqt.wq_from_file(gain_file)

	# convert data types to float
	num = convert_wq_dtypes(gain_df)  # TODO see if this step could be done in wq_from_file()

	# add source of wqp file (get's lost when the file gets averaged)
	wqt.addsourcefield(gain_df, "WQ_SOURCE", gain_file)

	# basename of the source gain file
	base = os.path.basename(gain_file)
	# try parsing the site from the filename
	try:
		# If it's a text code, use the text, otherwise call the function
		if isinstance(site, six.string_types):
			site = site.upper()
		else:
			site = site(filename=base, part=site_gain_params["site_part"])

		# lookup vert profile from site text
		session = classes.get_new_session()
		profile_site_id = profile_from_text(session, site)
		gain_df['Site'] = profile_site_id.id
		session.close()

	except ValueError:
		traceback.print_exc()

	# try parsing the gain setting from the filename
	try:
		# If gain setting the gain is provided use it, otherwise call the function
		if isinstance(gain, six.integer_types) or isinstance(gain, six.string_types):
			# strip all letters from gain setting ("GN10" -> 10)
			digits_only = ''.join(c for c in str(gain) if c in digits)
			gain_digits = int(digits_only)
			gain_df['Gain'] = gain_digits
		else:
			gain_setting_from_name = gain(filename=base, part=site_gain_params["gain_part"])
			digits_only = ''.join(c for c in str(gain_setting_from_name) if c in digits)
			gain_digits = int(digits_only)
			gain_df['Gain'] = gain_digits

	except ValueError:
		traceback.print_exc()

	# add row to database table vertical_profiles
	gain_wq_df2database(gain_df)
	return
