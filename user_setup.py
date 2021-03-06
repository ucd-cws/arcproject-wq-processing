from __future__ import print_function

import os
import sys
import subprocess

r_dependencies = ["RSQLite", "plyr", "gplots", "devtools", "ggplot2"]
r_github_dependencies = ["ucd-cws/wq-heatplot"]


def set_up_r_dependencies():
	import launchR  # imported here because it will be installed before this is called, but won't be installed at load time in all cases

	R = launchR.Interpreter()
	R.install_packages(["devtools"])
	R.run("-e", ["\"devtools::install_github('r-lib/remotes', ref = 'e56a41e1d0cad55cbe7d60b274b99ab7b7a76b5c')\"",])  # this is a hopefully temporary fix, which should make it so that the other packages install correctly. I believe wq-heatplot wasn't installing correctly without this.
	R.install_packages(r_dependencies, missing_only=False)
	R.install_github(r_github_dependencies)


def find_wheels(path):
	"""
		find any Python wheel files in the directory provided by "path". We build wheels and they are distributed alongside
		this file, so this loads and installs any wheels it finds.
	:param path:
	:return: list of files in the provided path
	"""

	return [f for f in os.listdir(path) if (os.path.isfile(os.path.join(path, f)) and f.endswith(".whl"))]


if __name__ == "__main__":

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

	set_up_r_dependencies()

	print("Installation complete")
