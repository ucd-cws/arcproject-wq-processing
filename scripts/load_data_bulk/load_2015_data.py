import os
from waterquality import classes
from scripts import slurp

### DEFINE DATA PATHS ###
base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
print(base_path)

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData" # or location on x drive


def jan():
	print("January 2014")

	path = os.path.join(data, "Jan_2014", "Arc_011314")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


	path = os.path.join(data, "Jan_2014", "Arc_011714")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def feb():
	print("Feburary 2014")
	path = os.path.join(data, "Feb_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'Arc_022814']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Feb_2014", "Arc_022814")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', ]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def mar():
	print("March 2014")
	path = os.path.join(data, "Mar_2014", "Arc_031714")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Mar_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'Arc_031714', 'Arc_032014']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def apr():
	print("April 2014")
	path = os.path.join(data, "Apr_2014", "Arc_042214")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	print("April 2014")
	path = os.path.join(data, "Apr_2014", "Arc_042114")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Apr_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII', 'Arc_042214', "Arc_042114"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def may():
	print("May 2014")
	path = os.path.join(data, "May_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	s.transect_gps_pattern = "*PosnPnt.shp" # included PosnPnt2.shp results in integrity error
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def jun():
	print("June 2014")
	path = os.path.join(data, "Jun_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def jul():
	print("July 2014")
	path = os.path.join(data, "Jul_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def aug():
	print("Aug 2014")
	path = os.path.join(data, "Aug_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII', "Arc_082614",  "Arc_082814"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


	print("Aug 2014")
	path = os.path.join(data, "Aug_2014", "Arc_082614")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	print("Aug 2014")
	path = os.path.join(data, "Aug_2014", "Arc_082814")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def sep():
	print("Sep 2014")
	path = os.path.join(data, "Sep_2014", "Arc_091514")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Sep_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII', "Arc_091514"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def oct():
	print("Oct 2014")
	path = os.path.join(data, "Oct_2014", "Arc_101314")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


	path = os.path.join(data, "Oct_2014", "Arc_101414")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


	path = os.path.join(data, "Oct_2014", "Arc_101714")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 3}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def nov():
	print("Nov 2014")
	path = os.path.join(data, "Nov_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def dec():
	print("Dec 2014")
	path = os.path.join(data, "Dec_2014")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

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