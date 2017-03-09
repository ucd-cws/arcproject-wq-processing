from arcproject.waterquality import classes
import os
import csv
# path to csv file
path = csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wqp_avgs.csv')

# # loop through rows of csv and add row to new remap objects
# f = open(csv_path)
# csv_f = csv.reader(f)
# header = next(csv_f, None)  # headers
# for row in csv_f:
# 	print(row)
# 	wq = classes.WaterQuality()
# 	wq.site_id = row[0]
# 	wq.date_time = row[1]
# 	wq.y_coord = row[2]
# 	wq.x_coord = row[3]
# 	wq.spatial_reference_code = row[4]
#
# 	print(wq)

from arcproject.scripts import chl_decision_tree
format_string = "%m/%d/%y %H:%M"
chl_decision_tree.load_data_from_csv(path, field_map=classes.water_quality_header_map,
                                     date_format_string=format_string, table_class=classes.WaterQuality)