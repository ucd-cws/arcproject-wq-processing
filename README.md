# arcproject-wq-processing
Water Quality Processing Pipeline for Arc of Delta Fishes Project

[![Code Issues](https://www.quantifiedcode.com/api/v1/project/5914c2c83c4042108a73af69c2c72573/badge.svg)](https://www.quantifiedcode.com/app/project/5914c2c83c4042108a73af69c2c72573)

Requires ArcGIS 10.4 or above or ArcGIS Pro 1.3 or above

## Building the installation package
_This section is for any future developers of this code base_. If you just want to use these tools, skip to the
section [Installing the code](#Installing-the-code).

The documentation on installing these tools refers to a zip file. These zip files are distributed as releases on this
repository. The master branch includes the latest release-ready code, and the zip packages are built using
the powershell script make_distribution.ps1 in this repository.

To start, clone the repository. Open up Powershell ISE on windows and navigate to the repository root folder in the console.
Then, run make_distribution.ps1. It will generate a new file named distribution.zip in the same folder. This zip file
contains a compiled Python wheel, the setup script (user_setup.py) and the python toolbox and metadata files.

## Installing the code
[Installation and Usage Information](https://github.com/ucd-cws/arcproject-wq-processing/wiki/installation)