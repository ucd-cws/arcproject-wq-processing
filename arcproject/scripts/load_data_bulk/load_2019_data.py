import os
from arcproject.scripts.load_data_bulk import slurp
from arcproject.scripts import wqt_timestamp_match

# path to location with data
data = r"C:\Users\dsx\Projects\arcproject\ARC_WQT_2019"  # or location on x drive


def rename_files(slurper):
	print("Renaming sites")
	files = slurper.find_files(data)
	for filepath in files:
		filepath_parts = os.path.split(filepath)
		filename_parts = filepath_parts[1].split("_")
		if filename_parts[2].endswith("1"):
			filename_parts[2] = filename_parts[2][:-1]  # strip the last character off if it's a 1
			filename = "_".join(filename_parts)
			newpath = os.path.join(filepath_parts[0], filename)
			print("Renaming {} to {}".format(filepath, newpath))
			os.rename(filepath, newpath)  # rename it now to remove the 1

def load_2019():
	print("Loading 2019 Data")
	path = data
	s = slurp.Slurper(instrument=wqt_timestamp_match.ysi)
	#rename_files(s)
	s.add_new_sites = True
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
