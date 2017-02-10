import subprocess
import os

from . import config

### DEFINE DATA PATHS ###
base_path = config.arcwqpro

# path to R exe
rscript_path = config.rscript
gen_heat = os.path.join(base_path, "scripts", "generate_heatplots.R")

subprocess.call([rscript_path, gen_heat, "--args", "CA", "salinity", "CA"])
