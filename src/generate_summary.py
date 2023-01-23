"""
Generate a summary of a data table, suitable for use with a matching chart.
generate_summary.py <path to CSV file> [--help]
"""
import numbers
from optparse import OptionParser
import re
import pandas

import pymannkendall as mk

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

def filter_to_time(row, name_column):
    # If all keys look like a time period, then can assume the values are a sorted time series.
    name = row[name_column]
    if is_string(name):
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        for quarter in quarters:
            if name.startswith(quarter):
                return True
        # like "2018/19"
        if re.search("^\d{4}/\d+$", name):
            return True
        # like "'10"
        if re.search("^'\d{2}$", name):
            return True
        # like "2024*" or "2024"
        if re.search("^\d{4}(\*)?$", name):
            return True
    if isinstance(name, numbers.Number):
        year = int(name)
        return year > 1000 and year < 3000 # year 3000 problem
    return False

def is_timeseries(df, name_column):
    # Could ask pandas.to_datetime, but it is bit too strict
    time_rows = df.apply(lambda row: filter_to_time(row, name_column), axis=1).dropna()
    time_rows = df[time_rows]
    return len(time_rows) == len(df)

def filter_to_percentages(row, value_column):
    value = row[value_column]
    return value.endswith('%')

def is_percentages(df, value_column):
    # Could ask pandas.to_datetime, but it is bit too strict
    rows = df.apply(lambda row: filter_to_percentages(row, value_column), axis=1).dropna()
    rows = df[rows]
    return len(rows) == len(df)

def filter_to_numeric(row, value_column):
    value = row[value_column]
    return isinstance(value, numbers.Number)

def are_values_all_numeric(df, value_column):
    numeric_rows = df.apply(lambda row: filter_to_numeric(row, value_column), axis=1).dropna()
    numeric_rows = df[numeric_rows]
    return len(numeric_rows) > 0

def remove_pc(value):
    if value.endswith('%'):
        return value[:-1]
    return float(value)

def format_value(value, is_percent):
    value = round(value, 2)
    if (is_percent):
        return f"{value}%"
    return value

def summarize(df):
    summary = []

    name_column = df.columns[0]
    value_column = df.columns[1]

    is_percent = False

    if not pandas.api.types.is_numeric_dtype(df[value_column]):
        if is_percentages(df, value_column):
            value_column_without_pc = value_column + " "
            df[value_column_without_pc] = df.apply(lambda row: remove_pc(row[value_column]), axis=1)
            df[value_column_without_pc] = df[value_column_without_pc].astype(float)
            df[value_column] = df[value_column_without_pc] # replace the data, so we keep the nice column name
            is_percent = True

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
            summary.append(f"{clean_name(row[name_column])} is in {place} place with {format_value(row[value_column], is_percent)} {make_lower(value_column)}")

            # bottom or top percentile
            # xxx
            # df.describe()["25%"]
            # df.describe()["75%"]

            interesting_names.append(row[name_column])
    else:
        # Many interesting items - so summarize them
        #
        interesting_average = df_interesting.mean(numeric_only=True)
        if (len(interesting_average) > 0):
            interesting_average = interesting_average[0]
            interesting_names_clean = []
            for _index, row in df_interesting_sorted.iterrows():
                interesting_names_clean.append(clean_name(row[name_column]))
                interesting_names.append(row[name_column])
            summary.append(f"{', '.join(interesting_names_clean)} had an average {format_value(interesting_average, is_percent)} {make_lower(value_column)}")
        else:
            for _index, row in df_interesting_sorted.iterrows():
                summary.append(f"{clean_name(row[name_column])} has {format_value(row[value_column], is_percent)} {make_lower(value_column)}")
                interesting_names.append(row[name_column])

    # max
    # TODO xxx support joint-max rows
    if are_values_all_numeric(df, value_column):
        max_row_value = df[value_column].max()
        max_row_name = df[name_column][df[value_column].idxmax()]

        if (max_row_name not in interesting_names):
            summary.append(f"{clean_name(max_row_name)} had highest {make_lower(value_column)} {format_value(max_row_value, is_percent)}")
    else:
        # TODO xxx - fallback
        summary.append("-")

    # top 3
    # xxx

    # bottom 3
    # xxx

    # average
    # xxx

    # Time-based charts
    if is_timeseries(df, name_column) and are_values_all_numeric(df, value_column):
        df_values = df[value_column]
        trend_test = mk.original_test(df_values, alpha=0.05)
        trend_desc = trend_test.trend
        if trend_desc == 'no trend':
            summary.append(f"No overall trend")
        else:
            summary.append(f"Overall trend is {trend_test.trend}")

    summary.append("")

    return '. '.join(summary)

summary = summarize(data)

print(summary)
