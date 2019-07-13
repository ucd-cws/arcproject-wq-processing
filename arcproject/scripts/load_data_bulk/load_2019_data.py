import os
from arcproject.scripts.load_data_bulk import slurp

# path to location with data
data = r"C:\Users\dsx\Projects\arcproject\ARC_WQT_2019"  # or location on x drive


def load_2019():
	print("Loading 2019 Data")
	path = data
	s = slurp.Slurper()
	s.add_new_sites = False
	s.dst = True
	s.skipext = [".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def main(month="ALL"):
	if month == "ALL":
		load_2019()
	else:
		month()

if __name__ == '__main__':
	main()
