import os
from arcproject.waterquality import classes
from arcproject.scripts.load_data_bulk import slurp

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData" # or location on x drive


def jan():
	print("January 2015")
	path = os.path.join(data, "Jan_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)


def feb():
	print("Feburary 2015")
	path = os.path.join(data, "Feb_2015")



def mar():
	print("March 2015")
	path = os.path.join(data, "Mar_2015")
	s = slurp.Slurper()


def apr():
	print("April 2015")
	path = os.path.join(data, "Apr_2015", "Arc_042214")
	s = slurp.Slurper()


def may():
	print("May 2015")
	path = os.path.join(data, "May_2015")
	s = slurp.Slurper()



def jun():
	print("June 2015")
	path = os.path.join(data, "Jun_2015")


def jul():
	print("July 2015")
	path = os.path.join(data, "Jul_2015")
	s = slurp.Slurper()

def aug():
	print("Aug 2015")
	path = os.path.join(data, "Aug_2015", "ARC_081215")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def sep():
	print("Sep 2015")
	path = os.path.join(data, "Sep_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def oct():
	print("Oct 2015")
	path = os.path.join(data, "Oct_2015", "Arc_100515")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 3}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def nov():
	print("Nov 2015")
	path = os.path.join(data, "Nov_2015", "ARC_110215")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Nov_2015", "ARC_111615")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def dec():
	print("Dec 2015")
	path = os.path.join(data, "Dec_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx", ".lyr"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
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
	main()
