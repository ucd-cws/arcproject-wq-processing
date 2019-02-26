"""
	Provides functions to find the R executable
"""

import os

import launchR

R = launchR.Interpreter()

r_packages = R.user_library
rscript = R.executable

# I think this line is to force it to always check the library folder we're using - can get confusing for R when it
# has multiple installs/libraries (I think)
os.environ["R_LIBS_USER"] = r_packages
