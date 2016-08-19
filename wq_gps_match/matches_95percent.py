import timestamp_match
import glob
import os

folder = os.path.join("examples", "Arc_040413_WQ")
print(folder)

wq_files = glob.glob(os.path.join(folder, "*wqt*.csv"))
print(wq_files)

gps = os.path.join("examples", "Arc_040413_GPS", "040413_PosnPnt.shp")

output = r"examples\Arc_040413_output"

for csv in wq_files:
	print(csv)
	percent = timestamp_match.match_metrics(csv, gps)

	if percent > 95:
		base = os.path.basename(csv)
		noext = os.path.splitext(base)[0]
		out = os.path.join(output, noext + '.shp')
		timestamp_match.main(csv, gps, out)
