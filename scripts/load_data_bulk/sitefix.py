from waterquality import classes
from scripts import swap_site_recs
import os
import csv

# path to csv with remaped site codes
csvpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sites_renamed.csv')
print(csvpath)

class Remap():
	current = None
	new = None
	note = None

remaps = []

# loop through rows of csv and add row to new remap objects
f = open(csvpath)
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



