__author__ = "ambell, nickrsan"

from distutils.core import setup

setup(
	name='arcproject-wq',
	version='0.9',
	packages=['scripts', 'waterquality'],
	license='MIT',
	description=None,
	long_description="",
	install_requires=["SQLAlchemy >= 1.1.2", "six", "numpy >= 1.9.2", "pandas >= 0.16.1", "matplotlib",
						"geodatabase_tempfile", "amaptor >= 0.1.1"],
	author=__author__,
	author_email="nrsantos@ucdavis.edu",
	url='https://github.com/ucd-cws/amaptor',
	include_package_data=True,
)
