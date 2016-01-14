import os, sys
import matplotlib.pyplot as plt
from matplotlib.mlab import csv2rec
import json
import csv
import datetime

legend = []

#function calls
def get_csv_column_count():
	with open('cpu.csv') as f:
	    reader = csv.reader(f, delimiter=',', skipinitialspace=True)
	    first_row = next(reader)
	    num_cols = len(first_row)

	return num_cols

def convertInt(val):
	try:
		a = float(val)
		return a
	except ValueError:
		return False

def get_y_axis():
	y = {}
	data_list = []
	i = 0

	with open('cpu.csv', 'rb') as f:
	    reader = csv.reader(f)
	    for row in reader:
	    	i = 1
	    	while i < get_csv_column_count():
		    	if convertInt(row[i]):
		    		data_list.append(float(row[i]))
		    	i+=1

	y['lower'] = min(data_list)
	y['upper'] = max(data_list)

	return y

def get_x_axis():
	x = {}
	data_list = []
	i = 0

	with open('cpu.csv', 'rb') as f:
	    reader = csv.reader(f)
	    for row in reader:
	    	if convertInt(row[i]):
	    		data_list.append(float(row[0]))

	x['lower'] = min(data_list)
	x['upper'] = max(data_list)

	return x

#write initial load test to csv
#pull cpu values from only 1st server in load balanced setup
rows = []
i = 1
increment = 4 #time increment is approx evey 4 seconds for a 10 minute test (150 data points per datadog request)

with open('cpu.json') as data_file:    
    data = json.load(data_file)

for row in data["series"][0]["pointlist"]:
	rows.append(row[1])

time_stamp = data["series"][0]["start"]
t = datetime.datetime.fromtimestamp(int(time_stamp/1000)).strftime('date_%m_%d_%H_%M')
legend.append(t);

header = ['time_stamp', legend[0]]
with open('cpu.csv', 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for row in rows:
    	writer.writerow([i*increment,row]) 
    	i+=1

#append 2nd load test data to csv
#pull cpu values from only 1st server in load balanced setup
rows = []

with open('cpu-2.json') as data_file:    
    data = json.load(data_file)

for row in data["series"][0]["pointlist"]:
	rows.append(row[1])

time_stamp = data["series"][0]["start"]
t = datetime.datetime.fromtimestamp(int(time_stamp/1000)).strftime('date_%m_%d_%H_%M')
legend.append(t);

csvfile = 'cpu.csv'
i = 0

with open(csvfile, 'r') as fin, open('new_'+csvfile, 'w') as fout:
    reader = csv.reader(fin)
    writer = csv.writer(fout)
    writer.writerow(next(reader) + [legend[1]] ) #add another heading for 2nd load test
    for row in reader:
    	try:
    		new_row = row
    		writer.writerow(new_row+[rows[i]])
    	except IndexError:
    		pass
    	i+=1

#rename file to original and delete second file
os.remove('cpu.csv')
os.rename('new_cpu.csv','cpu.csv')

#append 3rd load test data to csv
#pull cpu values from only 1st server in load balanced setup
rows = []

with open('cpu-3.json') as data_file:    
    data = json.load(data_file)

for row in data["series"][0]["pointlist"]:
	rows.append(row[1])

time_stamp = data["series"][0]["start"]
t = datetime.datetime.fromtimestamp(int(time_stamp/1000)).strftime('date_%m_%d_%H_%M')
legend.append(t);

csvfile = 'cpu.csv'
i = 0

with open(csvfile, 'r') as fin, open('new_'+csvfile, 'w') as fout:
    reader = csv.reader(fin)
    writer = csv.writer(fout)
    writer.writerow(next(reader) + [legend[2]] ) #add another heading for 2nd load test
    for row in reader:
    	try:
    		new_row = row
    		writer.writerow(new_row+[rows[i]])
    		i+=1
    	except IndexError:
    		pass

#rename file to original and delete second file
os.remove('cpu.csv')
os.rename('new_cpu.csv','cpu.csv')

# end mikes work

fname = 'cpu.csv'
load_test_data = csv2rec(fname)

# # These are the colors that will be used in the plot
color_sequence = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']

# You typically want your plot to be ~1.33x wider than tall. This plot
# is a rare exception because of the number of lines being plotted on it.
# Common sizes: (10, 7.5) and (12, 9)
fig, ax = plt.subplots(1, 1, figsize=(12, 14))

# # Remove the plot frame lines. They are unnecessary here.
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

# # Ensure that the axis ticks only show up on the bottom and left of the plot.
# # Ticks on the right and top of the plot are generally unnecessary.
ax.get_xaxis().tick_bottom()
ax.get_yaxis().tick_left()

# # Limit the range of the plot to only where the data is.
# # Avoid unnecessary whitespace.
xVal = get_x_axis()
yVal = get_y_axis()

plt.xlim(int(xVal['lower'])-1, int(xVal['upper'])+1)
plt.ylim(int(yVal['lower'])-.25, int(yVal['upper'])+1)

# # Make sure your axis ticks are large enough to be easily read.
# # You don't want your viewers squinting to read your plot.
plt.xticks(range(int(xVal['lower']), int(xVal['upper']), 4), fontsize=14)
plt.yticks(range(int(yVal['lower']), int(yVal['upper']), 1), ['{0}%'.format(x) for x in range(int(yVal['lower']), int(yVal['upper']), 1)], fontsize=14)

# # Provide tick lines across the plot to help your viewers trace along
# # the axis ticks. Make sure that the lines are light and small so they
# # don't obscure the primary data lines.
for y in range(1, int(yVal['upper']), 1):
    plt.plot(range(int(xVal['lower']), int(xVal['upper'])), [y] * len(range(int(xVal['lower']), int(xVal['upper']))), '--', lw=0.5, color='black', alpha=0.3)

# # Remove the tick marks; they are unnecessary with the tick lines we just
# # plotted.
plt.tick_params(axis='both', which='both', bottom='off', top='off', labelbottom='on', left='off', right='off', labelleft='on')

# # Now that the plot is prepared, it's time to actually plot the data!
# # Note that I plotted the legend in order of the highest % in the final year.
y_offsets = {legend[0]: 0.5, legend[1]: -0.5, legend[2]: -0.6}

for rank, column in enumerate(legend):
    # Plot each line separately with its own color.
    column_rec_name = column.replace('\n', '_').replace(' ', '_').lower()

    line = plt.plot(load_test_data.time_stamp,
                    load_test_data[column_rec_name],
                    lw=2.5,
                    color=color_sequence[rank])

    # Add a text label to the right end of every line. Most of the code below
    # is adding specific offsets y position because some labels overlapped.
    y_pos = load_test_data[column_rec_name][-1]

    # if column in y_offsets:
    #     y_pos += y_offsets[column]

#     # Again, make sure that all labels are large enough to be easily read
#     # by the viewer.
    plt.text(xVal['upper']+.5, y_pos, column, fontsize=14, color=color_sequence[rank])

# # Make the title big enough so it spans the entire plot, but don't make it
# # so big that it requires two lines to show.

# # Note that if the title is descriptive enough, it is unnecessary to include
# # axis labels; they are self-evident, in this plot's case.
plt.title('Load test comparison graph', fontsize=18, ha='center')

# # Finally, save the figure as a PNG.
# # You can also save it as a PDF, JPEG, etc.
# # Just change the file extension in this call.
plt.savefig('load-test-comparison.png', bbox_inches='tight')