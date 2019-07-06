class NoRecordsError(ValueError):
	pass


class SpatialReferenceError(ValueError):
	pass

class NoCoordinatesError(ValueError):
	"""
		Used to indicate that the WQ data doesn't have coordinates attached and no GPS track was provided
	"""
	pass