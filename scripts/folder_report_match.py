import glob
import os
import pandas
import wqt_timestamp_match

# these will be argv at some point?
export_shp = True
AP_data_folder = r"\\s1.cws.ucdavis.edu\projects\ArcProject\ArcProjectData"
output = r"testfiles\results"

# get current working directory
dir_path = os.path.dirname(os.path.realpath(__file__))


# data saved in folders named Mon_YEAR
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

		wq = wqt_timestamp_match.wq_append_fromlist(wq_transect_list)

		pts = wqt_timestamp_match.gps_append_fromlist(gps_list)

		if wq.shape != (0, 0) and pts.shape != (0, 0):
			# replace illegal fieldnames
			wq = wqt_timestamp_match.replaceIllegalFieldnames(wq)

			offsets = {}

			for i in [-1, -0.5, 0, 0.5, 1]:
				# offset water quality
				off = wqt_timestamp_match.dstadjustment(wq, i)

				# try joining by timestamp
				off_joined_data = wqt_timestamp_match.JoinByTimeStamp(off, pts)
				off_matches = wqt_timestamp_match.splitunmatched(off_joined_data)[0]

				# report the percentage matched
				percent_match = wqt_timestamp_match.JoinMatchPercent(wq, off_matches)

				# add to dict
				offsets[i] = percent_match

			# best match for the offsets
			highest_percent_offset = max(offsets, key=offsets.get)


			# apply offset to the original data
			offset_df = wqt_timestamp_match.dstadjustment(wq, highest_percent_offset)

			# join using time stamps w/ exact match
			joined_data = wqt_timestamp_match.JoinByTimeStamp(offset_df, pts)

			matches = wqt_timestamp_match.splitunmatched(joined_data)[0]

			no_geo = wqt_timestamp_match.splitunmatched(joined_data)[0]

			percent = wqt_timestamp_match.JoinMatchPercent(wq, matches)

			print("PERCENT MATCHED for folder: {}".format(percent))

			#save out the not a matches
			if no_geo.shape[0] > 0:
				print("There are unmatched records!")
				nonmatch_outname = os.path.join(dir_path, output, folder_name + '_NOTMATCHABLE.csv')
				print(nonmatch_outname)
				no_geo.to_csv(nonmatch_outname)

			if export_shp is True:
				print("Saving joined data as a shapefile....")
				# save merged to shapefile
				out = os.path.join(output, folder_name + '.shp')
				wqt_timestamp_match.geodf2shp(matches, out)

			result_summary.append([folder_name, len(wq_transect_list), len(gps_list), percent, highest_percent_offset])

	except:
		print("Problem with {}".format(folder))
		result_summary.append([folder_name, 0, 0, "ERROR", "ERROR"])


# save the results summary to a csv file
summary_df = pandas.DataFrame(result_summary, columns=["Folder", "NUM_WQ", "NUM_GPS", "MATCH", "DSTOFFSET"])
summary_df.to_csv("Folder_matches_summary.csv", index=False)
