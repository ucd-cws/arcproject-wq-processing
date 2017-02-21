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

		current_r_version = winreg.QueryValueEx(key, "Current Version")[0]

		winreg.CloseKey(registry)
	except WindowsError:
		raise WindowsError("Unable to get R path - Make sure R is installed on this machine!")

	major_version, minor_version, sub_version = current_r_version.split(".")
	packages_version = "{}.{}".format(major_version, minor_version)  # get the version format used for packages
	new_r_package_folder = os.path.join(r"C:{}".format(os.environ["HOMEPATH"]), "Documents", "R", "win-library", packages_version)
	return current_r_path, new_r_package_folder

r_folder, r_packages = get_r_folder()
rscript = os.path.join(r_folder, "bin", "Rscript.exe")
r = os.path.join(r_folder, "bin", "R.exe")

os.environ["R_LIBS_USER"] = r_packages
