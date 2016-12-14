import os
import arcpy
import glob
from sqlalchemy import exc
from scripts import wq_gain
from waterquality import utils
from waterquality import classes
from scripts import wqt_timestamp_match

### DEFINE DATA PATHS ###
base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
print(base_path)

# import the project's toolbox
arcpy.ImportToolbox(os.path.join(base_path, "wq-processing-toolbox.pyt"))

# path to location with data
data = r"C:\Users\Andy\Desktop\ArcData" # or location on x drive

### MAKE SITEs ###
print("Adding default sloughs to sites")
site_names = {"NS": "Nurse Slough",
			"MZ": "Montezuma Slough",
            "CC": "Calhoun Cut Canal",
            "CB": "Cabin Slough",
            "NSDV": "Nurse Slough DV",
            "SB": "",
            "BK": "",
            "CA": "",
            "HS": "",
            "LN": "",
            "BN": "",
            "SH": "",
            "UL": "Ulatis Creek"}

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
"LNCA": "LN", # CHECK
"BN1": "BN",
"BN2": "BN",
"SH1": "SH",
"SH4": "SH",
"SH5": "SH",
"SH7": "SH",
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

# Jan 2013
# gain files
"""gains_list = glob.glob(os.path.join(data, "Jan_2013", "*", "*", "*wqp*"))
print(gains_list)

for wq_gain_file in gains_list:
	try:
		basename = os.path.basename(wq_gain_file)
		site_id = basename.split("_")[3].upper() # site code is the forth part when split by underscores
		gain_setting = 0 # TODO check

		# find the shapefiles to try to match
		two_up = os.path.dirname(os.path.dirname(wq_gain_file))

		gps_pts = glob.glob(os.path.join(two_up, "*", "*ZoopChlW.shp"))[0]
		print("{} {} {} {}".format(basename, site_id, gain_setting, gps_pts))

		# run gain_wq function
		try:
			wq_gain.main(wq_gain_file, site_id, gain_setting, gps_pts)
		except exc.IntegrityError as e:
			arcpy.AddMessage("Unable to import gain file. Record for this gain file "
			                 "already exists in the vertical_profiles table.")

	except:
		print("Error")
"""
# water quality transects

transect_list = glob.glob(os.path.join(data, "Jan_2013", "Arc*", "*_WQ", "*wqt*"))
print(transect_list)

wqt = r'C:\\Users\\Andy\\Desktop\\ArcData\\Jan_2013\\Arc_010713\\Arc_010713_WQ\\Arc_010713_wqt_bk'
shp = r'C:\Users\Andy\Desktop\ArcData\Jan_2013\Arc_010713\Arc_010713_GPS\010713_PosnPnt.shp'

wqt_timestamp_match.main([wqt], shp)
