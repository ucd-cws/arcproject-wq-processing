"""
	@author: nickrsan
	@date: 2016/12/05 (YYYY/MM/DD)

	Designed to slurp in the backlog of WQ data using the existing code developed for this project.

	Overall strategy is a folder walk, with an attempt to understand which folders represent days in the field,
	which ones represent specific data of interest. May be able to just index some of this based on filenames though
"""

import re
import os

from scripts import wqt_timestamp_match





class Slurper(object):

	shapefile_match = "^.*PosnPnt.*\.shp$"
	shapefiles = []
	shapefile_index = {}

	def slurp(self, base_path):
		"""
			Given a path, traverses it looking for items to slurp in
		:return:
		"""
		self._walk(base_path)


	def _handle_shapefile(self, path):
		pass

	def _walk(self, base_path):
		"""
			Handles the actual directory traversal.
		:param base_path:
		:return:
		"""
		for root, dirs, files in os.walk(base_path):
			for l_file in files:
				if re.match(self.shapefile_match, l_file,) is not None:
					self._handle_shapefile(os.path.join(root, l_file))


### DEFINE DATA PATHS ###
base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
print(base_path)

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData" # or location on x drive