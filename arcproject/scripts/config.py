"""
Single file to collect all the configuration settings for the project.
"""

import os
import logging
import tempfile

from . import r_connector

log = logging.getLogger("arcproject")
log.setLevel(logging.DEBUG)
sth = logging.StreamHandler()
sth.setLevel(logging.DEBUG)
log.addHandler(sth)
fih = logging.FileHandler(tempfile.mktemp("arcproject_log"))
fih.setLevel(logging.DEBUG)
log.addHandler(fih)

# path to the arcproject-wq-processing folder
arcwqpro = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# path to reference lines for sloughs
ref_line = os.path.join(arcwqpro, "arcproject", "geo", "ArcLinearReferenceRoute_Lines.shp")

# location of r install
rscript = r_connector.rscript

# set the path to the arcproject folder as an environment variable to access from R
os.environ["arcproject_code_path"] = arcwqpro
projection_spatial_reference = 26942  # 3310  # Teale Albers  # 26942  # CA State Plane II Meters