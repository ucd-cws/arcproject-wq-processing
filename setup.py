from __future__ import print_function

__author__ = "ambell, nickrsan"

import os
import subprocess
try:
	import winreg
except ImportError:
	import _winreg as winreg

from setuptools import setup
from setuptools.command.install import install

import r_dependencies
new_r_package_folder = r"C:\arcproject_wq\r_packages"

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

		winreg.CloseKey(registry)
	except WindowsError:
		raise WindowsError("Unable to get R path - Make sure R is installed on this machine!")

	print("R located at {}".format(current_r_path))

	return os.path.join(current_r_path, "bin", "Rscript.exe")

try:
	r_exec = get_r_exec()
except WindowsError:
	raise WindowsError("R does not appear to be installed on this machine. Please install it, making sure to install with version number in registry (installation option) then try again")


def write_r_package_install_file():
	print("Installing R packages using interpreter at {}".format(r_exec))

	dependencies_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], "arcproject", "scripts",
									 "install_packages.R")
	with open(dependencies_file, 'wb') as rdeps:
		# for every item in the dependecies list, fill the values into the installation expression, and write that out to the file
		rdeps.write("install.packages(c({}), dependencies=TRUE, lib=\"{}\", repos='http://cran.us.r-project.org')".format(", ".join(r_dependencies.dependencies), new_r_package_folder.replace("\\", "\\\\")))

	return dependencies_file


dependencies_file = write_r_package_install_file()


class CustomInstallCommand(install):
	"""
	Make a custom command so we can execute the R package installation after package installation
	See https://blog.niteoweb.com/setuptools-run-custom-code-in-setup-py/ for why we're using this
	"""
	def run(self):
		install.run(self)  # call the parent class's default actions

		if not os.path.exists(new_r_package_folder):
			os.makedirs(new_r_package_folder)

		subprocess.call([r_exec, dependencies_file])  # call the code to set up R packages




setup(
	name='arcproject-wq',
	version='0.9',
	packages=['arcproject', 'arcproject.scripts', 'arcproject.waterquality'],
	license='MIT',
	description=None,
	long_description="",
	install_requires=["SQLAlchemy >= 1.1.2", "six", "numpy >= 1.9.2", "pandas >= 0.16.1", "matplotlib",
						"geodatabase_tempfile", "amaptor >= 0.1.1.2"],
	author=__author__,
	author_email="nrsantos@ucdavis.edu",
	url='https://github.com/ucd-cws/amaptor',
	include_package_data=True,
	cmdclass={
		'install': CustomInstallCommand,
	},
)
