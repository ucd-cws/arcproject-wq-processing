import os
from waterquality import classes
from scripts import slurp

### DEFINE DATA PATHS ###
base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
print(base_path)

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData" # or location on x drive


# def jan():
# 	print("January 2016")
#
# 	path = os.path.join(data, "Jan_2016")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = False
# 	s.site_function_params = {"site_part": 3, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)
#
#
def feb():
	print("Feburary 2016")
	path = os.path.join(data, "Feb_2016")
	s = slurp.Slurper()
	s.add_new_sites = True
	s.dst = True
	s.gain_pattern = "*WQ_*"
	s.skipext = [".csv", ".xlsx", ".xls", ".dbf", ".prj", ".shp", ".shx"]
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_022016"]
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)




# def mar():
# 	print("March 2016")
# 	path = os.path.join(data, "Mar_2016")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_031215"]
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)
#
# 	path = os.path.join(data, "Mar_2016", "Arc_031215")
# 	s = slurp.Slurper()
# 	s.gain_pattern = '*wq*'
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', ]
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)


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



#
# def may():
# 	print("May 2016")
# 	path = os.path.join(data, "May_2016")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.gain_pattern = "*WQ*"
# 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)
#
#
#
#
# # def jun():
# # 	print("June 2016")
# # 	path = os.path.join(data, "Jun_2016")
# # 	s = slurp.Slurper()
# # 	s.add_new_sites = True
# # 	s.dst = True
# # 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# # 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# # 	print("Adding gain files to database")
# # 	s.slurp_gains(path)
# # 	print("Adding water quality transects to database")
# # 	s.slurp_trans(path)
#
#
# def jul():
# 	print("July 2016")
# 	path = os.path.join(data, "Jul_2016", "ARC_071615_WQ")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# 	print("Adding water quality transects to database")
# 	s.slurp_trans(path)
#
# 	path = os.path.join(data, "Jul_2016", "ARC_072115_WQ")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)
#
#
# def aug():
# 	print("Aug 2016")
# 	path = os.path.join(data, "Aug_2016")
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
# #
# # def sep():
# # 	print("Sep 2016")
# # 	path = os.path.join(data, "Sep_2016")
# # 	s = slurp.Slurper()
# # 	s.add_new_sites = True
# # 	s.dst = True
# # 	s.site_function_params = {"site_part": 3, "gain_part": 4}
# # 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# # 	print("Adding gain files to database")
# # 	s.slurp_gains(path)
# # 	print("Adding water quality transects to database")
# # 	s.slurp_trans(path)
#
#
# def oct():
# 	print("Oct 2016")
# 	path = os.path.join(data, "Oct_2016")
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
#
# # def nov():
# # 	print("Nov 2016")
# # 	path = os.path.join(data, "Nov_2016")
# # 	s = slurp.Slurper()
# # 	s.add_new_sites = True
# # 	s.dst = True
# # 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# # 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# # 	print("Adding gain files to database")
# # 	s.slurp_gains(path)
# # 	print("Adding water quality transects to database")
# # 	s.slurp_trans(path)
# #
# #
# def dec():
# 	print("Dec 2016")
# 	path = os.path.join(data, "Dec_2016")
# 	s = slurp.Slurper()
# 	s.add_new_sites = True
# 	s.dst = True
# 	s.site_function_params = {"site_part": 2, "gain_part": 4}
# 	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'StatePlaneII']
# 	print("Adding gain files to database")
# 	s.slurp_gains(path)
# 	print("Adding water quality transects to database")
# 	s.slurp_trans(path)

# jan()
feb()
# mar()
# apr()
# may()
# jun()
# jul()
# aug()
# sep()
# oct()
# nov()
# dec()