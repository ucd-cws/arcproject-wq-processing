"""
	Reloads the database but also reloads the testing data so that development work can proceed. Should not be used in
	production!
"""
from __future__ import print_function

import os

from waterquality import utils
from waterquality import classes
from scripts import wqt_timestamp_match
from scripts import chl_decision_tree

utils.recreate_tables()

### DEFINE DATA PATHS ###
base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
wq_data = os.path.join(base_path, "scripts", "tests", "testfiles", "Arc_040413", "Arc_040413_WQ", "Arc_040413_wqt_cc.csv")
gps_data = os.path.join(base_path, os.path.split(os.path.split(os.path.abspath(__file__))[0])[0], "scripts", "tests", "testfiles", "Arc_040413", "Arc_040413_GPS", "040413_PosnPnt.shp")

### MAKE SITE FOR DATA ###
#site_code = "wqt"
print("Adding default sloughs to sites")
site_names = {"wqt": "Test Site"}

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
"TS1": "WQT"
}

session = classes.get_new_session()

for vp in vert_profiles:
	ps = classes.ProfileSite()
	ps.abbreviation = vp
	ps.slough = vert_profiles[vp]
	session.add(ps)
	session.commit()

session.close()

### LOAD WQ DATA ###
print("Loading Water Quality Data")
wqt_timestamp_match.main([wq_data,], gps_data,)

### LOAD REGRESSION DATA ###
print("Loading Regression Data")
regression_data = os.path.join(base_path, "data", "legacy", "lm_coeffs_rsquared", "legacy_coeffs_rsquared.csv")
chl_decision_tree.load_regression_data_from_csv(regression_data)

print("Done Loading Data")
