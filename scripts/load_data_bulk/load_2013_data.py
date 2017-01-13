import os
from waterquality import classes
from scripts import slurp

### DEFINE DATA PATHS ###
base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
print(base_path)

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData" # or location on x drive

### MAKE SITEs ###
print("Adding default sloughs to sites")
site_names = {"NS": "Nurse Slough",
			"MZ": "Montezuma Slough",
            "CC": "Calhoun Cut Canal",
            "CB": "Cabin Slough",
            "NSDV": "Nurse Slough DV",
            # "SB": "",
            # "BK": "",
            # "CA": "",
            # "HS": "",
            # "LN": "",
            # "BN": "",
            # "SH": "",
            # "UL": "Ulatis Creek",
            # "DV": "",
            # "LC": "",
            # "CO": "",
            # "SI": "",
            # "BR": "",
            # "CACHE": "Cache",
            # "SI7": "",  # check
              }

session = classes.get_new_session()
for site in site_names:
	site_code = site
	if session.query(classes.Site).filter(classes.Site.code == site_code).one_or_none() is None:
		new_site = classes.Site()
		new_site.code = site_code
		new_site.name = site_names[site]
		session.add(new_site)
		session.commit()

session.close()

### Add vertical profile default sites ###
print("Adding default vertical profiles to profile_sites")
vert_profiles = {
"MZ1": "MZ",
"NS3": "NS",
"CA1": "CA",
"CS3": "CS",
"HS1": "HS",
"UL1": "UL",
"CC1": "CC",
"BK1": "BK",
# "LNCA": "LN",  # CHECK
# "BN1": "BN",
# "BN2": "BN",
# "SH1": "SH",
# "SH2": "SH",
# "SH4": "SH",
# "SH5": "SH",
# "SH6": "SH",
# "SH7": "SH",
# "BK0": "BK",
# "CA3": "CA",
# "LN2": "LN",
# "UL0": "UL",
# "DV1": "DV",
# "LCW": "LCW",
# "NS3": "NS",
# "SB1": "SB",
# "LC": "LC",
# "BK": "BK", # check
# "CC": "CC", # check
# # "BR1": "BR",
# # "BR2": "BR",
# # "SI1": "SI",
# # "SI2": "SI",
# # "SI4": "SI",
# # "SI6": "SI",
# # "SI7": "SI",
# # "NSDV": "NSDV",
# # "BK2": "BK", # check
# # "LN3": "LN",
# # "LC1": "LC",
# # "LC2": "LC"
}

session = classes.get_new_session()
for vp in vert_profiles:
	if session.query(classes.ProfileSite).filter(classes.ProfileSite.abbreviation == vp).one_or_none() is None:
		ps = classes.ProfileSite()
		ps.abbreviation = vp
		ps.slough = vert_profiles[vp]
		session.add(ps)
		session.commit()
session.close()


#############################################################


##### JAN ######
def jan():
	print("January 2013")

	jan = os.path.join(data, "Jan_2013")
	s = slurp.Slurper()

	# gain file like "Arc_010713_wqp_cs3" and all gain settings should be zero
	s.site_function_params = {"site_part": 3}
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', 'Arc_011813'] # weird site names for this folder
	s.gain_setting = 0

	print("Adding gain files to database")
	s.slurp_gains(jan)
	print("Adding water quality transects to database")
	s.slurp_trans(jan)





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
	s.exclude = ['StatePlaneCAII', 'SummaryFiles', "Arc_030413"]  # see github issue
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
