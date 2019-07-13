import load_2013_data
import load_2014_data
import load_2015_data
import load_2016_data
import load_2019_data
import sitefix
import grab_parse_siteid

# # load data
load_2013_data.main()
load_2014_data.main()
load_2015_data.main()
load_2016_data.main()
load_2019_data.main()

# site fix
sitefix.main()

# grab parse
grab_parse_siteid.main()