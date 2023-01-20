"""
Generate a summary of a data table, suitable for use with a matching chart.
generate_summary.py <path to CSV file> [--help]
"""
from optparse import OptionParser

import util_file

#usage() - prints out the usage text, from the top of this file :-)
def print_usage():
    print(__doc__)

parser = OptionParser(usage=__doc__)
# parser.add_option("-t", "--threshold", dest="threshold", default=100,
#     help="Threshold below which, an image is considered to be blurry")

(options, args) = parser.parse_args()

if len(args) != 1:
    print_usage()
    exit(1)

INPUT_FILEPATH = args[0]

data = util_file.read_csv_file(INPUT_FILEPATH)

def filter_to_asterisk(row, name_column):
    if '*' in row[name_column]:
        return True

    return False

def clean_name(name):
    return name.replace('*', '')

def summarize(df):
    summary = []

    name_column = df.columns[0]
    value_column = df.columns[1]

    # rows of interest (*)
    df_interesting = df.apply(lambda row: filter_to_asterisk(row, name_column), axis=1).dropna()
    df_interesting = df[df_interesting]
    df_interesting_sorted = df_interesting.sort_values(by=value_column, ascending=False)

    interesting_names = []
    for _index, row in df_interesting_sorted.iterrows():
        summary.append(f"{clean_name(row[name_column])} has {row[value_column]} {value_column.lower()}")
        interesting_names.append(row[name_column])

    # max
    max_row = df.max()

    max_row_name = max_row[name_column]
    max_row_value = max_row[value_column]

    if (max_row_name not in interesting_names):
        summary.append(f"{clean_name(max_row_name)} had highest {value_column.lower()} {max_row_value}")

    # top 3
    # df['percent'] = (df[column_int] / df2[column_int].sum()) * 100
	# df_sorted = df.sort_values(by=column_int, ascending=False)

    summary.append("")

    return '. '.join(summary)

summary = summarize(data)

print(summary)
