import os
from waterquality import classes
from scripts import slurp

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData" # or location on x drive


def jan():
	print("January 2016")

	path = os.path.join(data, "Jan_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = "*WQ_*"
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_022016"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def feb():
	print("Feburary 2016")
	path = os.path.join(data, "Feb_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = "*WQ_*"
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_022016"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def mar():
	print("March 2016")
	path = os.path.join(data, "Mar_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def apr():
	print("April 2016")
	path = os.path.join(data, "Apr_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def may():
	print("May 2016")
	path = os.path.join(data, "May_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def jun():
	print("June 2016")
	path = os.path.join(data, "Jun_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr", ".mxd"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def jul():
	print("July 2016")
	path = os.path.join(data, "Jul_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def aug():
	print("Aug 2016")
	path = os.path.join(data, "Aug_2016", "Arc_082316")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Aug_2016", "Arc_082416")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def sep():
	print("Sep 2016")
	path = os.path.join(data, "Sep_2016", "092716")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Sep_2016", "092816")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def oct():
	print("Oct 2016")
	path = os.path.join(data, "Oct_2016", "102516")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Oct_2016", "102616")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def nov():
	print("Nov 2016")
	path = os.path.join(data, "Nov_2016", "111816")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Nov_2016", "112016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def dec():
	print("Dec 2016")
	path = os.path.join(data, "Dec_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	s.gain_pattern = '*WQ_*'
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def main(month="ALL"):
	if month == "ALL":
		jan()
		feb()
		mar()
		apr()
		may()
		jun()
		jul()
		aug()
		sep()
		oct()
		nov()
		dec()
	else:
		month

if __name__ == '__main__':
	main(jan())