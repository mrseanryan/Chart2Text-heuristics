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

def is_string(item):
    return isinstance(item, str)

def filter_to_asterisk(row, name_column):
    if is_string(row[name_column]):
        if '*' in row[name_column]:
            return True

    return False

def clean_name(name):
    if is_string(name):
        return name.replace('*', '')
    return name

def make_lower(name):
    # xxx exclude abbreviations like US, U.S.
    if is_string(name):
        return name.lower()
    return name

def summarize(df):
    summary = []

    name_column = df.columns[0]
    value_column = df.columns[1]

    # rows of interest (*)
    df_interesting = df.apply(lambda row: filter_to_asterisk(row, name_column), axis=1).dropna()
    df_interesting = df[df_interesting]
    df_interesting_sorted = df_interesting.sort_values(by=value_column, ascending=False)
    # xxx use one or two randomly:
    # done - value
    # xxx at xth place
    # xxx above/below average
    # xxx More than X less than Y
    
    interesting_names = []
    if (len(df_interesting_sorted) <= 2):
        for _index, row in df_interesting_sorted.iterrows():
            place = df.index[df[name_column] == row[name_column]].tolist()
            summary.append(f"{clean_name(row[name_column])} is in {place} place with {row[value_column]} {make_lower(value_column)}")

            # bottom or top percentile
            # xxx
            # df.describe()["25%"]
            # df.describe()["75%"]

            interesting_names.append(row[name_column])
    else:
        # Many interesting items - so summarize them
        #
        # TODO xxx handle % values - need convert, create new column...
        interesting_average = df_interesting.mean(numeric_only=True)
        if (len(interesting_average) > 0):
            interesting_average = interesting_average[0]
            interesting_names_clean = []
            for _index, row in df_interesting_sorted.iterrows():
                interesting_names_clean.append(clean_name(row[name_column]))
                interesting_names.append(row[name_column])
            summary.append(f"{', '.join(interesting_names_clean)} had an average {interesting_average} {make_lower(value_column)}")
        else:
            for _index, row in df_interesting_sorted.iterrows():
                summary.append(f"{clean_name(row[name_column])} has {row[value_column]} {make_lower(value_column)}")
                interesting_names.append(row[name_column])

    # max
    max_row = df.max()

    max_row_name = max_row[name_column]
    max_row_value = max_row[value_column]

    if (max_row_name not in interesting_names):
        summary.append(f"{clean_name(max_row_name)} had highest {make_lower(value_column)} {max_row_value}")

    # top 3
    # xxx

    # bottom 3
    # xxx

    # average
    # xxx

    # Time-based charts
    # Trend for last 3 items ("Trend since 'Q3'")
    # "Large increase/decrease in '<last period>'"
    # "Large increase/decrease in '<last period>'"
    # "No significant change in '<last period>'"
    # xxx

    summary.append("")

    return '. '.join(summary)

summary = summarize(data)

print(summary)
