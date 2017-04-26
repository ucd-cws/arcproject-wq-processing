from __future__ import print_function

__author__ = "ambell, nickrsan"

try:
	from arcproject import __version__ as version
except ImportError:
	version = '2017.4.25'

from setuptools import setup


if __name__ == "__main__":
	setup(
		name='arcproject-wq',
		version=version,
		packages=['arcproject', 'arcproject.scripts', 'arcproject.waterquality'],
		license='MIT',
		description=None,
		long_description="",
		install_requires=["SQLAlchemy >= 1.1.2", "six",
							"geodatabase_tempfile", "amaptor >= 0.1.1.7", "launchR >= 0.3.0"],
						## "pandas >= 0.16.1", "matplotlib", and "numpy >= 1.9.2" also needed, but cause issues on ArcGIS 10.4 install where it tries to upgrade numpy
		author=__author__,
		author_email="nrsantos@ucdavis.edu",
		url='https://github.com/ucd-cws/amaptor',
		include_package_data=True,
	)
