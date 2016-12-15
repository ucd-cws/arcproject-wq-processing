import os
from waterquality import classes
from scripts import slurp_globber


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

##### JAN ######

jan = os.path.join(data, "Jan_2013")

s = slurp_globber.Slurper()
s.gain_setting = 0
s.filename_part_site = 3
s.slurp_gains(jan)
s.slurp_trans(jan)



##### FEB ######

feb = os.path.join(data, "Feb_2013")
s = slurp_globber.Slurper()
s.filename_part_site = 3
s.gain_setting = 0
s.slurp_gains(feb)