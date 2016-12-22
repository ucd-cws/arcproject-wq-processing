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


class Slurper(object):

	def __init__(self):
		# default settings for slurper
		self.exclude = ['StatePlaneCAII', 'SummaryFiles']  # folder to exclude from the pattern matching
		self.gain_pattern = '*wqp*' # pattern to match to find the gain water quality files
		self.transect_pattern = '*wqt*'  # pattern to match to find the transect water quality files
		self.transect_gps_pattern = '*PosnPnt.shp'  # pattern to find the water quality transect GPS files
		self.zoop_shp_pattern = '*ZoopChlW.shp'  # pattern to find the ZoopChl gps files to join with the gains
		self.dst = False  # adjust for daylight saving time
		self.site = wq_gain.profile_function_historic  # if provided overrides parsing filename
		self.gain_setting = wq_gain.profile_function_historic  # if provided overrides parsing filename


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

	def slurp_gains(self, base_path):
		zoop_files = self.find_files(base_path, self.zoop_shp_pattern, self.exclude)
		for gain_file in self.find_files(base_path, self.gain_pattern, self.exclude):
			try:
				wq_gain.main(gain_file, self.site, self.gain_setting, zoop_files)
			except exc.IntegrityError:
				print("Gain file already in database.")
			except Exception as e:
				print(e)
		pass

	def slurp_trans(self, base_path):

		transect_gps = self.find_files(base_path, self.transect_gps_pattern, self.exclude)
		wq_files = self.find_files(base_path, self.transect_pattern, self.exclude)

		print(wq_files, transect_gps)

		# TODO fix the site_function to allow user to specify the index with the site name

		wqt_timestamp_match.main(wq_files, transect_gps, output_feature=None,
		                         site_function=wqt_timestamp_match.site_function_historic, dst_adjustment=self.dst)

		pass
