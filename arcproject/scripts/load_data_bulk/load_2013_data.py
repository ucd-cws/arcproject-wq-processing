import os
from arcproject.waterquality import classes
from arcproject.scripts import slurp

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData"


def dec():
	print("December 2013")
	path = os.path.join(data, "Dec_2013")
	s = slurp.Slurper()
	# gain file like "arc_12113_wqp_ln2_gn1"
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.add_new_sites = True
	# daylight saving adjustment
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)


def nov():
	print("November 2013")
	path = os.path.join(data, "Nov_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.add_new_sites = True
	s.dst = True
	# exclude the shapefile in Arc_111313_GPS since it messs with the gain site mathc
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'Arc_111313_GPS']
	s.slurp_gains(path)
	s.slurp_trans(path)


def oct():
	print("October 2013")
	path = os.path.join(data, "Oct_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'Arc_101513_GPS', 'Arc_101713_GPS']
	s.add_new_sites = True
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)


def sep():
	print("September 2013")
	path = os.path.join(data, "Sep_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 3, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	s.add_new_sites = True
	s.dst = True
	print("Adding gain files to database")
	s.slurp_gains(path)
	print("Adding water quality transects to database")
	s.slurp_trans(path)


def aug():
	print("August 2013")
	path = os.path.join(data, "Aug_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	s.add_new_sites = True
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)


def jul():
	print("July 2013")
	path = os.path.join(data, "Jul_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	s.add_new_sites = True
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)


def jun():
	print("June 2013")

	# Arc_060313
	path = os.path.join(data, "Jun_2013", "Arc_060313")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 2}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	s.add_new_sites = True
	s.gain_setting = 0
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)


	# The other folders in June
	path = os.path.join(data, "Jun_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 3, "gain_part": 0}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_060313"]  # see above
	s.add_new_sites = True
	s.gain_setting = 0
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)


def may():
	print("May 2013")
	path = os.path.join(data, "May_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 2, "gain_part": 4}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	s.transect_gps_pattern = '*PosnPnt*.shp'
	s.gain_setting = 0
	s.add_new_sites = True
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)


def apr():
	print("April 2013")

	path = os.path.join(data, "Apr_2013", "Arc_040113")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 2}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']
	s.add_new_sites = True
	s.gain_setting = 0
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)


	# The other folders in april
	path = os.path.join(data, "Apr_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 3, "gain_part": 0}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_040113"]  # see above
	s.add_new_sites = True
	s.gain_setting = 0
	s.dst = True
	s.slurp_gains(path)
	s.slurp_trans(path)

def mar():
	print("March 2013")
	path = os.path.join(data, "Mar_2013")
	s = slurp.Slurper()
	s.exclude = ['StatePlaneCAII', 'SummaryFiles']  # see github issue
	s.site_function_params = {"site_part": 3}
	s.gain_setting = 0
	s.dst = True
	s.add_new_sites = True
	s.slurp_gains(path)
	s.slurp_trans(path)


def feb():
	print("Feb 2013")
	path = os.path.join(data, "Feb_2013", "Arc_020713")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 3}
	s.gain_setting = 0
	s.dst = True
	s.add_new_sites = True
	s.slurp_gains(path)
	s.slurp_trans(path)

	# folders for site part 2
	s = slurp.Slurper()
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_020713"]
	path = os.path.join(data, "Feb_2013")
	s.site_function_params = {"site_part": 2}
	s.gain_setting = 0
	s.dst = True
	s.add_new_sites = True
	s.slurp_gains(path)
	s.slurp_trans(path)


def jan():
	print("Jan 2013")
	path = os.path.join(data, "Jan_2013")
	s = slurp.Slurper()
	s.site_function_params = {"site_part": 3}
	s.gain_setting = 0
	s.dst = True
	s.add_new_sites = True
	s.slurp_gains(path)
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
