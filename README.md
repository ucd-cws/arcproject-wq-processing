# arcproject-wq-processing
Water Quality Processing Pipeline for Arc of Delta Fishes Project

## Overarching Workflow
(to move to Wiki once we have some actual code and info)

Python will be used for the main processing pipeline. Processing starts after data is differentially corrected and we can export an MXD to edit for the transect heatmaps.

For now, keep ArcGIS to as few functions as possible - only the map document creation/export if possible. Processing should be in as pure of functions as we can, and any tools are just to chain together functions.

We can build unit tests as our first interface, and then as the project proceeds, build scripts that leverage the functions, toolboxes where necessary, or some other way to interact with the code.

Database-wise, it'd be nice to use PostGIS, but we want to keep this serverless, so maybe Spatialite works? Worth investigating because it enables some of the ideas any has, and we can still use an ORM like SQLAlchemy.


## Interfaces

1. Load data to database
	- slurp in backcatalog of all data
		- sites
		- data for sites
	- Transect files - have the location
	- Create Sites
		- transect - single observations behind the boat
		- point location - vertical profiles at these spots - usually at start or end of transects
	- Vertical Profile/Gain
		- three different gain values = each as separate files
		- should they be associated with a shapefile
	- Lab values - regression based on these, but store these values too.
	- Modern 
2. Correct chlorophyll profiles (Question: how quickly do these data come back?)
3. View data in the database - SQLite Browser of some sort? Or dumping data as CSVs.
4. R scripts that retrieve data from DB to create heatplots
	- need to be referenced along transects
	- save specific spot for transect
	- run tool, overwrites heatplot for location with most current data
5. Static maps


## Site structure in database

Profiles (probably) get averaged and come back as one record - attached to a site ID - this is attached to a transect
Transects become the master site location 

Transect is parent table to a values table, as well as to a table of profile locations (associate with that transect).
The table of profile locations has its own table of values, looked up separately