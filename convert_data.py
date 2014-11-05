#!/usr/bin/env python3
import operator, string

# files
input_file = "raw_data.csv"

# sorting values
country_index = 1
start_point = 2
split_point = 16

# data
in_heading = []
x_heading = []
y_heading = []
data_table = []
sorted_x_weights = []
sorted_y_weights = []
result_count = 0

# country values
country_count = {}
country_feature = {}
country_math = {}

# force directed layout pairs
result_pairs = {}

# cleaning
remove_punct_map = dict.fromkeys(map(ord, string.punctuation))
def clean(in_str):
	return in_str.translate(remove_punct_map).replace("\n","")

def weight(clean_answer):
	if (clean_answer == "Very confident"):
		return 1
	return 0

def add_result(answer):
	clean_answers = []
	for x in range( 0, len(answer) ):
		clean_answers.append( clean(answer[x]) )


	global country_count
	global country_feature
	global country_math
	global result_pairs
	for x in range( 0, len(data_table) ):
		if clean_answers[country_index] in country_count:
			country_count[clean_answers[country_index]] += 1
		else:
			country_count[clean_answers[country_index]] = 1
			country_feature[clean_answers[country_index]] = 0
			country_math[clean_answers[country_index]] = 0

		if (clean_answers[start_point+x] == "Yes"):
			for y in range( 0, len(data_table[0]) ):
				answer_weight = weight(clean_answers[split_point+y])
				data_table[x][y] += answer_weight
				country_math[clean_answers[country_index]] += answer_weight
			country_feature[clean_answers[country_index]] += 1
			for another_x in range( x+1, len(data_table) ):
				if (clean_answers[start_point+another_x] == "Yes"):
					result_pairs[(x, another_x)] = result_pairs[(x, another_x)] + 1



def load_matrix(fname):
	f = open(fname, "r")

	# read file
	lines_list = f.readlines()
	data = [[str(val) for val in line.split(",")] for line in lines_list]

	print("data has %d columns" % len(data[0]))

	# get column headings
	remove_punct_map = dict.fromkeys(map(ord, string.punctuation))
	for x in range( 0, len(data[0]) ):
		in_heading.append( clean(data[0][x]) )

	print(in_heading)

	# initialise data table size
	for x in range( start_point, split_point ):
		columns = []
		for a in range( split_point, len(data[0]) ):
			columns.append(0)
		data_table.append(columns)
		x_heading.append(in_heading[x])

	for y in range( split_point, len(data[0]) ):
		y_heading.append(in_heading[y])

	print("\n\n")
	print(x_heading)
	print("\n\n")
	print(y_heading)
	print("\n\n")

	for x1 in range( 0, len(data_table) ):
		for x2 in range( x1+1, len(data_table) ):
			result_pairs[(x1, x2)] = 0



	# parse each instance
	global result_count
	result_count = len(data) - 1
	for x in range( 1, len(data) ):
		add_result(data[x])



	sort_data()
	print(sorted_x_weights)
	print(sorted_y_weights)
	print(data_table)
	print(result_count)


def sort_data():
	x_weights = {}
	y_weights = {}
	for x in range( 0, len(data_table) ):
		weight = 0
		for y in range( 0, len(data_table[x]) ):
			weight += (y+1) * data_table[x][y]
		x_weights[x] = weight

	for y in range( 0, len(data_table[0]) ):
		weight = 0
		for x in range( 0, len(data_table) ):
			weight += (x+1) * data_table[x][y]
		y_weights[y] = weight

	global sorted_x_weights
	global sorted_y_weights
	sorted_x_weights = sorted(x_weights.items(), key=operator.itemgetter(1))
	sorted_y_weights = sorted(y_weights.items(), key=operator.itemgetter(1))

def sorted_value(x, y):
	return data_table[sorted_x_weights[x][0]][sorted_y_weights[y][0]]


def write_heatmap_labels():
	out = open("heatmap_labels.csv", "w")
	out.write("label_name\n")
	for x in range( 0, len(x_heading) ):
		out.write("%s\n" % x_heading[sorted_x_weights[x][0]])
	for y in range( 0, len(y_heading) ):
		out.write("%s\n" % y_heading[sorted_y_weights[y][0]])

def write_heatmap():
	write_heatmap_labels()
	out = open("heatmap_data.csv", "w")
	out.write("x,y,z\n")

	for x in range( 0, len(data_table) ):
		for y in range( 0, len(data_table[x]) ):
			out.write("%d,%d,%d\n" % (x, y, sorted_value(x, y)))

def write_geomap():
	out = open("geomap_data.csv", "w")
	out.write("country,x,y\n")

	for key, value in country_count.items():
		out.write("%s,%f,%f\n" % (key, country_feature[key]/value, country_math[key]/value))

def write_graph():
	out = open("force_data.csv", "w")
	out.write("source,target,value\n")

	global result_count
	for key, value in result_pairs.items():
		out.write("%s,%s,%f\n" % (x_heading[key[0]], x_heading[key[1]], (10*value/result_count)-5))


load_matrix(input_file)
write_heatmap()
write_geomap()
write_graph()