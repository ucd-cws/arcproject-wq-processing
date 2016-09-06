import timestamp_match
import glob
import os
import pandas

# these will be argv at some point?
export_shp = True
AP_data_folder = r"\\s1.cws.ucdavis.edu\projects\ArcProject\ArcProjectData"
output = r"examples\results"

# get current working directory
dir_path = os.path.dirname(os.path.realpath(__file__))


# data saved in folders named Mon_YEAR
#data_folders_glob = glob.glob(os.path.join(AP_data_folder, "*_201[0-9]", "Arc_[0-9]*"))
data_folders_glob = glob.glob(os.path.join(AP_data_folder, "*_201[0-9]"))
date_folders = []
for d in data_folders_glob:
	if os.path.isdir(d) == True:
		date_folders.append(d)


result_summary = []

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
			if notamatch.shape[0] > 0:
				print("There are unmatched records!")
				nonmatch_outname = os.path.join(dir_path, output, folder_name + '_NOTMATCHABLE.csv')
				notamatch.to_csv(nonmatch_outname)

			if export_shp is True:
				print("Saving joined data as a shapefile....")
				# save merged to shapefile
				out = os.path.join(output, folder_name + '.shp')
				timestamp_match.write_shp(out, matches)

				# copy projection from source
				timestamp_match.copyPRJ(gps_list[0], out)

			result_summary.append([folder_name, len(wq_transect_list), len(gps_list), percent, highest_percent_offset])

	except:
		print("Problem with {}".format(folder))
		result_summary.append([folder_name, 0, 0, "ERROR", "ERROR"])


# save the results summary to a csv file
summary_df = pandas.DataFrame(result_summary, columns=["Folder", "NUM_WQ", "NUM_GPS", "MATCH", "DSTOFFSET"])
summary_df.to_csv("Folder_matches_summary.csv", index=False)
