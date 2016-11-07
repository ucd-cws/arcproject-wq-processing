# use python (via subprocess) to create heatplot in R

import pandas as pd
import subprocess
import os

# set wd to Arcproject-wq-processing scripts folder
wd = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname("__file__"))))
print(wd)


###############################################################
# data needs to be in a csv file (path passed to r)

# example data
transect_wq = os.path.join(wd, r"tests\testfiles\Arc_BKwqtCHL_example.csv")
transect_df = pd.read_csv(transect_wq, parse_dates=[0], na_values=["NaT", "NaN"])

# save example to temporary csv
temp = os.path.join(wd, "temp.csv")
transect_df.to_csv(temp, index=False)


##############################################################

data = temp
dateField = "Date"
distanceField = "Distance"
wqVariable = "CHL"
title = "CHL test"
output = os.path.join(wd, "test1.png")


# path to heatplot.R file that creates heatplots
Rfilename = os.path.join(wd, "heatplot.R")

# path to R exe
rscript_path = r"C:\Program Files\R\R-3.2.3\bin\rscript.exe" # TODO set automatically?


# BELOW ASSUMES RScript IS A SYSTEM PATH VARIABLE
p = subprocess.call([rscript_path, Rfilename, data, dateField, distanceField, wqVariable, title, output])