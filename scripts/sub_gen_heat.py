import subprocess
import os

### DEFINE DATA PATHS ###
base_path = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]

# path to R exe
rscript_path = r"C:\Program Files\R\R-3.2.3\bin\rscript.exe"
gen_heat = os.path.join(base_path, "scripts\generate_heatplots.R")

subprocess.call([rscript_path, gen_heat, "--args", "CA", "salinity", "CA"])
