from arcproject.scripts import SpatialReferenceError, NoRecordsError


def get_wq_df_spatial_reference(df):
	sr_codes = df.spatial_reference_code.unique()  # get all of the codes in use in this query
	if sr_codes.size > 1:  # if we have more than one code, sound the alarm
		raise SpatialReferenceError("Records have non-matching spatial reference - can't map.")
	elif sr_codes.size == 1:
		sr_code = sr_codes[0]  # get what should be the only item in the sr_codes array
	else:  # aka, if sr_codes.size == 0
		if df.size == 0:
			raise NoRecordsError("No records for query")
		else:
			raise SpatialReferenceError("No Spatial Reference attached to records in query - can't map!")

	return sr_code