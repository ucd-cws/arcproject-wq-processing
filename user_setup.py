from __future__ import print_function

import os
import sys
import subprocess

r_dependencies = ["\"RSQLite\"", "\"plyr\"", "\"gplots\"", "\"ggplot2\""]

try:
	import winreg
except ImportError:
	import _winreg as winreg


def get_r_exec():
	"""
		We make this a function and call it first because setuptools just puts "error:none" if it errors out inside the
		main setup call. So, check before doing any other installation, which seems like a good idea anyway.
	:return:
	"""
	try:
		registry = winreg.ConnectRegistry("", winreg.HKEY_LOCAL_MACHINE)  # open the registry
		# current_r_version = winreg.QueryValue(registry, r"Software\R-core\R\Current Version")  # get the PISCES location
		key = winreg.OpenKey(registry, r"Software\R-core\R")
		current_r_path = winreg.QueryValueEx(key, "InstallPath")[0]
		current_r_version = winreg.QueryValueEx(key, "Current Version")[0]

		winreg.CloseKey(registry)
	except WindowsError:
		raise WindowsError("Unable to get R path - Make sure R is installed on this machine!")

	print("R located at {}".format(current_r_path))

	major_version, minor_version, sub_version = current_r_version.split(".")
	packages_version = "{}.{}".format(major_version, minor_version)  # get the version format used for packages
	new_r_package_folder = os.path.join(os.environ["USERPROFILE"], "Documents", "R", "win-library", packages_version)
	return os.path.join(current_r_path, "bin", "Rscript.exe"), new_r_package_folder


def write_r_package_install_file(r_exec, new_r_package_folder):
	print("Installing R packages using interpreter at {}. This may take some time".format(r_exec))

	dependencies_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], "install_packages.R")
	with open(dependencies_file, 'w') as rdeps:
		# for every item in the dependecies list, fill the values into the installation expression, and write that out to the file
		rdeps.write(
			"install.packages(c({}), dependencies=TRUE, lib=\"{}\", repos='http://cran.us.r-project.org')".format(
				", ".join(r_dependencies), new_r_package_folder.replace("\\", "\\\\")))

	return dependencies_file


def set_up_r_dependencies(new_r_package_folder, r_exec):
	if not os.path.exists(new_r_package_folder):
		os.makedirs(new_r_package_folder)

	dependencies_file = write_r_package_install_file(r_exec=r_exec, new_r_package_folder=new_r_package_folder)

	try:
		subprocess.check_output([r_exec, dependencies_file],
								stderr=subprocess.STDOUT)  # call the code to set up R packages
	except subprocess.CalledProcessError as e:
		print(
			"Installation of R packages failed {}.\nR Package installer output the following while processing:\n{}".format(
				e.returncode, e.output))
		sys.exit(1)


def find_wheels(path):
	"""
		find any Python wheel files in the directory provided by "path"
	:param path:
	:return: list of files in the provided path
	"""

	return [f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f.endswith(".whl"))]


if __name__ == "__main__":
	try:
		r_exec, new_r_package_folder = get_r_exec()
	except WindowsError:
		raise WindowsError(
			"R does not appear to be installed on this machine. Please install it, making sure to install with version number in registry (installation option) then try again")

	print("Removing old versions of the code, if they exist.")
	subprocess.call([sys.executable, "-m", "pip", "uninstall", "arcproject_wq", "-q"])

	try:
		subprocess.check_output([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		print("arcproject package install failed {}.\nInstaller output the following while processing:\n{}".format(
			e.returncode, e.output))
		sys.exit(1)

	install_folder = os.path.split(os.path.abspath(__file__))[0]
	for wheel in find_wheels(install_folder):
		print("Install wheel file {}".format(wheel))
		try:
			subprocess.check_output([sys.executable, "-m", "pip", "install", os.path.join(install_folder, wheel)],
									stderr=subprocess.STDOUT)  # should install requirements too
		except subprocess.CalledProcessError as e:
			print("arcproject package install failed {}.\nInstaller output the following while processing:\n{}".format(
				e.returncode, e.output))
			sys.exit(1)

	set_up_r_dependencies(new_r_package_folder, r_exec)

	print("Installation complete")
