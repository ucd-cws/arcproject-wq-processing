"""
Single file to collect all the configuration settings for the project.
"""

import os

# path to the arcproject-wq-processing folder
arcwqpro = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# path to reference lines for sloughs
ref_line = os.path.join(arcwqpro, "geo", "Reference_SloughCenterlines.shp")