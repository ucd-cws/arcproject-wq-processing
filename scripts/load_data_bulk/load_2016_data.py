import os
from waterquality import classes
from scripts import slurp

### DEFINE DATA PATHS ###
base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
print(base_path)

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData" # or location on x drive


def jan():
	print("January 2015")

	path = os.path.join(data, "Jan_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = False
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	print("Adding gain files to database")
	s.slurp_gains(path)


def feb():
	print("Feburary 2015")
	path = os.path.join(data, "Feb_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_022015"]
	print("Adding gain files to database")
	s.slurp_gains(path)

	path = os.path.join(data, "Feb_2015", "Arc_022015")
	s = slurp.Slurper()
	s.gain_pattern = '*wq*'
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', ]
	print("Adding gain files to database")
	s.slurp_gains(path)


def mar():
	print("March 2015")
	path = os.path.join(data, "Mar_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_031215"]
	print("Adding gain files to database")
	s.slurp_gains(path)

	path = os.path.join(data, "Mar_2015", "Arc_031215")
	s = slurp.Slurper()
	s.gain_pattern = '*wq*'
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', ]
	print("Adding gain files to database")
	s.slurp_gains(path)


def apr():
	print("April 2015")
	path = os.path.join(data, "Apr_2015", "Arc_042815")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = '*WQ*'
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)

	path = os.path.join(data, "Apr_2015", "Arc_043015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = 'ARC*'
	s.site_function_params = {"site_part": 2, "gain_part": 3}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)


def may():
	print("May 2015")
	path = os.path.join(data, "May_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = "*WQ*"
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)




# def jun():
# 	print("June 2015")
# 	path = os.path.join(data, "Jun_2015")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)
# 	print("Adding water quality transects to database")
# 	s.slurp_trans(path)


def jul():
	print("July 2015")
	path = os.path.join(data, "Jul_2015", "ARC_071615_WQ")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding water quality transects to database")
	s.slurp_trans(path)

	path = os.path.join(data, "Jul_2015", "ARC_072115_WQ")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)


def aug():
	print("Aug 2015")
	path = os.path.join(data, "Aug_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


#
# def sep():
# 	print("Sep 2015")
# 	path = os.path.join(data, "Sep_2015")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.site_function_params = {"site_part": 3, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)
# 	print("Adding water quality transects to database")
# 	s.slurp_trans(path)


def oct():
	print("Oct 2015")
	path = os.path.join(data, "Oct_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)



# def nov():
# 	print("Nov 2015")
# 	path = os.path.join(data, "Nov_2015")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)
# 	print("Adding water quality transects to database")
# 	s.slurp_trans(path)
#
#
def dec():
	print("Dec 2015")
	path = os.path.join(data, "Dec_2015")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)

# jan()
# feb()
# mar()
# apr()
# may()
# jun()
# jul()
# aug()
# sep()
# oct()
# nov()
dec()