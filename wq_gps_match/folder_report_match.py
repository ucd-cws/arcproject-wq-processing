import timestamp_match
import glob
import os
import pandas
#import csv # TODO both pandas and CSV packages called to_csv  - causing issues!!!

AP_data_folder = r"\\s1.cws.ucdavis.edu\projects\ArcProject\ArcProjectData"

# data saved in folders named Mon_YEAR
#data_folders_glob = glob.glob(os.path.join(AP_data_folder, "*_201[0-9]", "Arc_[0-9]*"))
data_folders_glob = glob.glob(os.path.join(AP_data_folder, "*_201[0-9]"))
date_folders = []
for d in data_folders_glob:
	if os.path.isdir(d) == True:
		date_folders.append(d)

output = r"\examples\results"

date_folders = [r"\\s1.cws.ucdavis.edu\projects\ArcProject\ArcProjectData\Jan_2014"]

results_csv = []
try:
	# get list of all water quality transects *wqt* with glob in folder
	for folder in date_folders:
		folder_name = os.path.basename(os.path.normpath(folder))

		try:
			wq_transect_list = glob.glob(os.path.join(folder, "Arc_*", "*WQ", "*wqt*"))

			# use points that are diff corrected - in the monthly summary folder
			gps_list = glob.glob(os.path.join(folder, "SummaryFiles", "*GPS", "*PosnPnt.shp"))

			#print(wq_transect_list)

			print("WQ: {}, GPS: {}, folder: {}".format(len(wq_transect_list), len(gps_list), folder_name))

			wq = timestamp_match.wq_append_fromlist(wq_transect_list)

			pts = timestamp_match.gps_append_fromlist(gps_list)

			if wq.shape != (0, 0) and pts.shape != (0, 0):
				# replace illegal fieldnames
				wq = timestamp_match.replaceIllegalFieldnames(wq)

				offsets = {}

				for i in [-1, -0.5, 0, 0.5, 1]:
					#print("Time offset: {} hour".format(i))

					# offset water quality
					off = timestamp_match.dstadjustment(wq, i)

					# try joining by timestamp
					matches = timestamp_match.JoinByTimeStamp(off, pts)[0]

					# report the percentage matched
					percent_match = timestamp_match.JoinMatchPercent(wq, matches)
					#print("{} %".format(percent_match))

					# add to dict
					offsets[i] = percent_match

				#print(offsets)
				highest_percent_offset = max(offsets, key=offsets.get)
				#print(highest_percent_offset)

				#apply offset
				offset_df = timestamp_match.dstadjustment(wq, highest_percent_offset)
				offset_df.head()

				# join using time stamps w/ exact match
				joined_data = timestamp_match.JoinByTimeStamp(offset_df, pts)

				matches = joined_data[0]

				notamatch = joined_data[1]

				percent = timestamp_match.JoinMatchPercent(wq, matches)

				print("PERCENT MATCHED for folder: {}".format(percent))

				#save out the not a matches
				try:
					print("Notamatch: {}".format(notamatch.shape))
					nonmatch_outname = folder_name + '_NOTMATCHABLE.csv'

					notamatch.to_csv("jan2014.csv")
					notamatch.to_csv(os.path.join(output, nonmatch_outname))

					# save merged to shapefile
					# save match to to shp
					# out = os.path.join(output, folder_name + '.shp')
					# timestamp_match.write_shp(out, matches)

					# copy projection from source
					# timestamp_match.copyPRJ(gps_list[0], out)


				except:
					print("Unable to save matches as shapefile or non-matches as csv")

				results_csv.append([folder_name, len(wq_transect_list), len(gps_list), percent, highest_percent_offset])
		except:
			print("Problem with {}".format(folder))
			results_csv.append([folder_name, 0, 0, "ERROR", "ERROR"])
except:
	print("ERROR: unable to finish")

"""
with open('WaterQuality_Folder_matches.csv', 'wb') as csvfile:
	w = csv.writer(csvfile)
	w.writerow(["Folder", "NUM_WQ", "NUM_GPS", "MATCH", "DSTOFFSET"])

	for r in results_csv:
		w.writerow(r)

"""