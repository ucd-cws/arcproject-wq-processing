"""
	Provides functions to find the R executable
"""

import os

import launchR

R = launchR.Interpreter()

r_packages = R.user_library
rscript = R.executable

os.environ["R_LIBS_USER"] = r_packages
