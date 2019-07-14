1. Fix field names - can maybe use wqt_timestamp_match.ReplaceIllegalFieldnames for this
    - lots of names with dashes or spaces. Probably worth an explicit rename
        field map though, rather than renaming certain characters (spaces, percents,
        hyphens, degree symbols, etc, because then we end up with potentially unknown
        fields)
2. Need to make sure ArcGIS can absorb DMS, or convert to DD
    - Use DMS to DD function to make POINT_X and POINT_Y fields like the GPS
        previously added
    - use MakeXYEventLayer to make a new point layer, or can we skip that
        because we just needed the coordinates anyway? We may need to do it
        because we'll want to project it and store the projected values
    - need a new function to make points from fields, then save out a new
        feature class, then feed it through the rest of the process (sans-joining)
    - what is the datum used by the Sonde? Waiting for response from
3. Check on if it strips off the headers - does it find the correct header line
4. Make sure it can import without GPS data - needs to become optional in the tool,
    - and if it isn't provided, the tool should validate that the input file has
        coordinate information before running further
    - Workflow-wise, should we assume "Lat" and "Lon" are the fields, or should
        we have a field name option in the tool
        
5. Do we need to correct this data, and if we don't, will our other items work on
    non-corrected data? I think they let you select any variable, but worth
    confirming.
    
6. Need to add "instrument" to wq gain profiles - used in wq_gain.main. Check that the "site" should
also equal "profile_function_historic"