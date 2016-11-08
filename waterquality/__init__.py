import six

def shorten_float(original, places=8):
	"""
	Used in order to make floats a consistent length for unit tests - it's OK to shorten them because with 8
	decimal places we should be able to test if the code is functioning correctly. Beyond that the small specifics probably
	aren't super important
	:param original: The original number
	:param places: The number of decimal places to shorten it to (obeys rounding rules)
	:return: new number with specified number of decimal places
	"""
	format_str = "{0:." + six.text_type(places) + "f}"
	return float(format_str.format(original))