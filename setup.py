__author__ = "ambell, nickrsan"

from setuptools import setup

setup(
	name='arcproject-wq',
	version='0.9',
	packages=['arcproject', 'arcproject.scripts', 'arcproject.waterquality'],
	license='MIT',
	description=None,
	long_description="",
	#requires=["SQLAlchemy", "six", "numpy >= 1.9.2", "pandas >= 0.16.1", "matplotlib",
	#					"geodatabase_tempfile", "amaptor >= 0.1.1.0"],
	author=__author__,
	author_email="nrsantos@ucdavis.edu",
	url='https://github.com/ucd-cws/amaptor',
	include_package_data=True,
)
