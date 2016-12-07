import pandas

df = pandas.read_csv(r"C:\Users\dsx.AD3\Code\arcproject-wq-processing\scripts\tests\testfiles\Arc_040413\Arc_040413_WQ\Arc_040413_wqp_bk1.csv",
					 header=9,
					 parse_dates=[[0,1]],
					 na_values='#')

for row in df.iterrows():
	keys = row[1].index  # iterrows gives us a 2-item tuple. First is row ID, second is the data as a Pandas Series.
	#  The attribute "index" of that series is an index object, but we can use it like a list of keys

	for key in keys:
		row[1].get(key)