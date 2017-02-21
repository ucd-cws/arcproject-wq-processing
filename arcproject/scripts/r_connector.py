"""
	Provides functions to find the R executable
"""
try:
	import winreg
except ImportError:
	import _winreg as winreg

import os

def get_r_folder():
	try:
		registry = winreg.ConnectRegistry("", winreg.HKEY_LOCAL_MACHINE)  # open the registry
		# current_r_version = winreg.QueryValue(registry, r"Software\R-core\R\Current Version")  # get the PISCES location
		key = winreg.OpenKey(registry, r"Software\R-core\R")
		current_r_path = winreg.QueryValueEx(key, "InstallPath")[0]

		winreg.CloseKey(registry)
	except:
		raise WindowsError("Unable to get R path")

	return current_r_path

r_folder = get_r_folder()
rscript = os.path.join(r_folder, "bin", "Rscript.exe")
r = os.path.join(r_folder, "bin", "R.exe")
