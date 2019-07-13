"""
	Appears to change the site tags of certain files that were named in known nonstandard ways
"""

from arcproject.scripts import swap_site_recs
import os
import csv


class Remap():
	current = None
	new = None
	note = None


def main():

	csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sites_renamed.csv')
	remaps = []

	# loop through rows of csv and add row to new remap objects
	f = open(csv_path)
	csv_f = csv.reader(f)
	header = next(csv_f, None) # headers
	for row in csv_f:
		if row[0] != '' and row[1] != '':
			r = Remap()
			r.current = row[0]
			r.new = row[1]
			if row[2] != '':
				r.note = row[2]
			remaps.append(r)

	for t in remaps:
		try:
			print("Transfering {} to {} with note {}".format(t.current, t.new, t.note))
			swap_site_recs.main(t.current, t.new, True, t.note)
		except Exception as e:
			print(e)

if __name__ == '__main__':
	# path to csv with remaped site codes
	main()
