"""
	@author: nickrsan
	@date: 2016/12/05 (YYYY/MM/DD)

	Designed to slurp in the backlog of WQ data using the existing code developed for this project.

	Overall strategy is a folder walk, with an attempt to understand which folders represent days in the field,
	which ones represent specific data of interest. May be able to just index some of this based on filenames though
"""
import os
from scripts import wqt_timestamp_match
from scripts import wq_gain
import fnmatch
from sqlalchemy import exc
from sqlalchemy.orm.exc import NoResultFound
# import project modules
from waterquality import classes
import six


class Slurper(object):

	def __init__(self):
		# default settings for slurper
		self.exclude = ['StatePlaneCAII', 'SummaryFiles']  # folder to exclude from the pattern matching
		self.gain_pattern = '*wqp*'  # pattern to match to find the gain water quality files
		self.transect_pattern = '*wqt*'  # pattern to match to find the transect water quality files
		self.transect_gps_pattern = '*PosnPnt.shp'  # pattern to find the water quality transect GPS files
		self.zoop_shp_pattern = '*ZoopChlW.shp'  # pattern to find the ZoopChl gps files to join with the gains
		self.dst = False  # adjust for daylight saving time
		self.site = wq_gain.profile_function_historic  # if provided overrides parsing filename
		self.gain_setting = wq_gain.profile_function_historic  # if provided overrides parsing filename
		self.site_function_params = {"site_part": 2,
                                     "gain_part": 4}  # parsing the site codes and gains using underscores
		self.add_new_sites = False  # adds unknown sites to the database

	def find_files(self, directory, pattern='*', exclude=None):
		"""http://stackoverflow.com/questions/14798220/how-can-i-search-sub-folders-using-glob-glob-module-in-python"""
		if not os.path.exists(directory):
			raise ValueError("Directory not found {}".format(directory))

		matches = []
		for root, dirnames, filenames in os.walk(directory):
			skipfolders = exclude
			dirnames[:] = [d for d in dirnames if d not in skipfolders]

			for filename in filenames:
				full_path = os.path.join(root, filename)
				if fnmatch.filter([full_path], pattern):
					matches.append(os.path.join(root, filename))
		return matches

	def check_wqp_names(self, filename, add=False):
		# validates profile codes against database before trying to import gain file
		if isinstance(self.site, six.string_types):
			site_code = self.site.upper()
		else:
			base = os.path.basename(filename)
			site_code = self.site(filename=base, part=self.site_function_params["site_part"])

		# new database session
		try:
			session = classes.get_new_session()
			q = session.query(classes.ProfileSite).filter(classes.ProfileSite.abbreviation == site_code).one()
		except NoResultFound:
			if add:
				# when true add unknown vertical profile code as a new profile site
				ps = classes.ProfileSite()
				ps.abbreviation = site_code
				session.add(ps)
				session.commit()
				print("Adding profile site code [{}] to vertical_profiles.".format(site_code))
			else:
				raise ValueError("Vertical profile site code [{}] not found.".format(site_code))
		finally:
			session.close()
		return

	def slurp_gains(self, base_path):

		zoop_files = self.find_files(base_path, self.zoop_shp_pattern, self.exclude)
		sites_shp_df = wqt_timestamp_match.gps_append_fromlist(zoop_files)

		for gain_file in self.find_files(base_path, self.gain_pattern, self.exclude):
			print(gain_file)
			# validate that we have the site in VerticalProfile table
			self.check_wqp_names(gain_file, self.add_new_sites)

			try:
				wq_gain.main(gain_file, site=self.site, gain=self.gain_setting, sample_sites_shp=sites_shp_df,
				             site_gain_params=self.site_function_params)
			except exc.IntegrityError as e:
				print(e)
				print("Gain file already in database.")
			except Exception as e:
				print(e)
		pass

	def check_wqt_site_codes(self, filename, site_func_params, add=False):
		# validates site codes against database before trying to import transect
		base = os.path.basename(filename)
		site_part = site_func_params.get("site_part")
		# split basename into parts using the underscore as deliminator
		site_code = base.split("_")[int(site_part)].upper()

		# new database session
		try:
			session = classes.get_new_session()
			q = session.query(classes.Site).filter(classes.Site.code == site_code).one()
		except NoResultFound:
			if add:
				new_site = classes.Site()
				new_site.code = site_code
				session.add(new_site)
				session.commit()
				print("Site code [{}] added to sites table.".format(site_code))
			else:
				raise ValueError("Site code [{}] not found.".format(site_code))
		finally:
			session.close()
		return

	def slurp_trans(self, base_path):

		transect_gps = self.find_files(base_path, self.transect_gps_pattern, self.exclude)
		wq_files = self.find_files(base_path, self.transect_pattern, self.exclude)

		#print(wq_files, transect_gps)
		for wq in wq_files:
			print(wq)
			self.check_wqt_site_codes(wq, self.site_function_params, self.add_new_sites)

		wqt_timestamp_match.main(wq_files, transect_gps, output_feature=None,
		                         site_function=wqt_timestamp_match.site_function_historic,
		                         site_func_params=self.site_function_params,
		                         dst_adjustment=self.dst)
		pass

