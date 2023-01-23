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

# show min and previous 2
def summarize_decreasing_ts(df, name_column, value_column, is_percent):
    summary = []
    # TODO xxx support joint-min rows
    # TODO xxx show next 2
    min_row_value = df[value_column].min()
    min_row_name = df[name_column][df[value_column].idxmin()]

    summary.append(f"{clean_name(min_row_name)} had lowest {make_lower(value_column)} {format_value(min_row_value, is_percent)}")
    return summary

# show max and following 2
def summarize_increasing_ts(df, name_column, value_column, is_percent):
    summary = []
    # TODO xxx support joint-max rows
    # TODO xxx show next 2
    max_row_value = df[value_column].max()
    max_row_name = df[name_column][df[value_column].idxmax()]

    summary.append(f"{clean_name(max_row_name)} had highest {make_lower(value_column)} {format_value(max_row_value, is_percent)}")
    return summary

# show max and following 2
def summarize_non_ts(df, name_column, value_column, is_percent):
    summary = []
    # TODO xxx support joint-max rows
    max_row_value = df[value_column].max()
    max_row_name = df[name_column][df[value_column].idxmax()]

    summary.append(f"{clean_name(max_row_name)} had highest {make_lower(value_column)} {format_value(max_row_value, is_percent)}")
    return summary

def convert_to_sortable_time(time_value):
    if is_string(time_value):
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        for quarter in quarters:
            if time_value.startswith(quarter):
                remaining_parts = time_value.split(' ')[1:]
                remaining_parts_as_time = []
                for part in remaining_parts:
                    remaining_parts_as_time.append(convert_to_sortable_time(part))
                # have quarters last. assumption: remainder is some kind of year.
                remaining_parts_as_time.append(quarter)
                return ' '.join(remaining_parts_as_time)
        # like "2018/19"
        if re.search("^\d{4}/\d+$", time_value):
            return time_value
        # like "'10"
        if re.search("^'\d{2}$", time_value):
            year_2_digit = int(time_value[1:])
            if year_2_digit >= 70:
                return f"19{year_2_digit}"
            if year_2_digit >= 0 and year_2_digit <= 9:
                return f"200{year_2_digit}"
            return f"20{year_2_digit}"
        # like "2024*" or "2024"
        if re.search("^\d{4}(\*)?$", time_value):
            return time_value.replace('*', '')
    return time_value

def add_time_column(df, name_column, time_column):
    df[time_column] = df.apply(lambda row: convert_to_sortable_time(row[name_column]), axis=1)

def list_with_and(names):
    names_but_last = names[:-1]
    text = ', '.join(names_but_last)
    return f"{text} and {names[len(names)-1]}"

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
    df_interesting_sorted = df_interesting.sort_values(by=name_column, ascending=True)
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
            summary.append(f"{list_with_and(interesting_names_clean)} had an average {format_value(interesting_average, is_percent)} {make_lower(value_column)}")
        else:
            for _index, row in df_interesting_sorted.iterrows():
                summary.append(f"{clean_name(row[name_column])} has {format_value(row[value_column], is_percent)} {make_lower(value_column)}")
                interesting_names.append(row[name_column])

    is_all_numeric = are_values_all_numeric(df, value_column)

    # Time-based charts
    is_increasing = False
    is_decreasing = False
    if is_all_numeric:
        if is_timeseries(df, name_column):
            # need to sort by time, increasing
            time_column = 'time_'
            df_tmp = df.copy()
            add_time_column(df_tmp, name_column, time_column)
            df_tmp = df_tmp.sort_values(by=time_column, ascending=True)

            df_values = df_tmp[value_column].values
            trend_test = mk.original_test(df_values, alpha=0.05)
            trend_desc = trend_test.trend
            if trend_desc == 'no trend':
                summary.append(f"No overall trend")
            else:
                first_period = df_tmp[name_column].values[0]
                last_period = df_tmp[name_column].values[len(df)-1]
                summary.append(f"{first_period} to {last_period} has an overall {trend_test.trend} trend")
                if trend_test.trend == 'increasing':
                    is_increasing = True
                else:
                    if trend_test.trend == 'decreasing':
                        is_decreasing = True
            # trend + decreasing -> show min and previous 2
            if is_decreasing:
                summary = summary + summarize_decreasing_ts(df_tmp, name_column, value_column, is_percent)
            # no trend OR trend + increasing -> show max and following 2
            else:
                summary = summary + summarize_increasing_ts(df_tmp, name_column, value_column, is_percent)

        else: # not timeseries
            # -> show max and following 2
            summary = summary + summarize_non_ts(df, name_column, value_column, is_percent)
    else:
        # fallback
        summary.append("-")

    summary.append("")

    return '. '.join(summary)

summary = summarize(data)

print(summary)
