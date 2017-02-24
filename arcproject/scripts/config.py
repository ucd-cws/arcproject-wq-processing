"""
Single file to collect all the configuration settings for the project.
"""

import os
from . import r_connector

# path to the arcproject-wq-processing folder
arcwqpro = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# path to reference lines for sloughs
ref_line = os.path.join(arcwqpro, "arcproject", "geo", "ArcLinearReferenceRoute_Lines.shp")

# location of r install
rscript = r_connector.rscript

# set the path to the arcproject folder as an environment variable to access from R
os.environ["arcproject_code_path"] = arcwqpro
