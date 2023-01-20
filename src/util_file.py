import pandas

def read_csv_file(filepath):
    data = pandas.read_csv(filepath)
    return data
