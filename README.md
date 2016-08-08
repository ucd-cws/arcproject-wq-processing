# arcproject-wq-processing
Water Quality Processing Pipeline for Arc of Delta Fishes Project

## Overarching Workflow
(to move to Wiki once we have some actual code and info)

Python will be used for the main processing pipeline. Processing starts after data is differentially corrected and we can export an MXD to edit for the transect heatmaps.

For now, keep ArcGIS to as few functions as possible - only the map document creation/export if possible. Processing should be in as pure of functions as we can, and any tools are just to chain together functions.

We can build unit tests as our first interface, and then as the project proceeds, build scripts that leverage the functions, toolboxes where necessary, or some other way to interact with the code.

Database-wise, it'd be nice to use PostGIS, but we want to keep this serverless, so maybe Spatialite works? Worth investigating because it enables some of the ideas any has, and we can still use an ORM like SQLAlchemy.
