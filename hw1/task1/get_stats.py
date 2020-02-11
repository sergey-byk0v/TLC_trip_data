import pandas as pd
from pandas.errors import ParserError
import numpy as np
import subprocess


def convert_type_function(type_to_convert, return_if_exception=None):
    def return_function(x):
        try:
            x = type_to_convert(x)
        except ValueError:
            return None
        else:
            return return_if_exception
    return return_function


def read_value_data(path):
    invalid_count = 0
    while True:
        try:
            data = pd.read_csv(path)
        except ParserError as error:
            invalid_count += 1

            error_line = str(error).split()[str(error).split().index('line') + 1][:-1]

            command = f"sed -i {error_line}d {path}"
            subprocess.call(command.split())
        else:
            return data, invalid_count


def general_stats(path):
    gen_stat = {}
    data, invalid_rows = read_value_data(path)
    data.columns = np.vectorize(lambda s: s.lower())(data.columns)

    data['lpep_dropoff_datetime'] = data['lpep_dropoff_datetime'].apply(convert_type_function(np.datetime64))
    invalid_rows += data['lpep_dropoff_datetime'].isna().sum()
    data = data.dropna(subset=['lpep_dropoff_datetime'])

    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].apply(convert_type_function(np.datetime64))
    invalid_rows += data['lpep_pickup_datetime'].isna().sum()
    data = data.dropna(subset=['lpep_pickup_datetime'])

    data['trip_distance'] = data['trip_distance'].apply(convert_type_function(float))
    invalid_rows += data['trip_distance'].isna().sum()
    data = data.dropna(subset=['trip_distance'])

    data['total_amount'] = data['total_amount'].apply(convert_type_function(float))
    invalid_rows += data['total_amount'].isna().sum()
    data = data.dropna(subset=['total_amount'])

    data['passenger_count'] = data['passenger_count'].apply(convert_type_function(int))
    invalid_rows += data['passenger_count'].isna().sum()
    data = data.dropna(subset=['passenger_count'])

    gen_stat['mean_cost'] = data['total_amount'].mean()
    data['trip_duration'] = data['lpep_dropoff_datetime'] - data['lpep_pickup_datetime']
    longest = data['trip_duration'].max()
    gen_stat['longest_ride'] = longest

    pickup_times = pd.DataFrame(data['lpep_pickup_datetime'])
    if pickup_times.shape[0] != 0:
        pickup_times.index = pickup_times['lpep_pickup_datetime']
        max_count_start = pickup_times['lpep_pickup_datetime'].resample('10T').count().idxmax()
        max_count = pickup_times['lpep_pickup_datetime'].resample('10T').count().max()
        max_count_end = max_count_start + np.timedelta64(10, 'm')
        gen_stat['max_count'] = max_count
        gen_stat['max_count_start'] = max_count_start
        gen_stat['max_count_end'] = max_count_end

    gen_stat['invalid_rows'] = invalid_rows
    gen_stat['count'] = data.shape[0]
    gen_stat = pd.DataFrame(gen_stat, index=[0])
    return gen_stat


def missing_dates(path):

    missing_date = pd.Series()
    data, _ = read_value_data(path)
    data.columns = np.vectorize(lambda s: s.lower())(data.columns)

    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].apply(to_datetime)
    data = data.dropna(subset=['lpep_pickup_datetime'])

    data['lpep_dropoff_datetime'] = data['lpep_dropoff_datetime'].apply(to_datetime)
    missing_date = missing_date.append(
        data['lpep_pickup_datetime'].iloc[np.where(data['lpep_dropoff_datetime'].isna())[0]].apply(lambda i: i.date()),
        ignore_index=True)

    data['trip_distance'] = data['trip_distance'].apply(to_float)
    missing_date = missing_date.append(
        data['lpep_pickup_datetime'].iloc[np.where(data['trip_distance'].isna())[0]].apply(lambda i: i.date()),
        ignore_index=True)

    data['total_amount'] = data['total_amount'].apply(to_float)
    missing_date = missing_date.append(
        data['lpep_pickup_datetime'].iloc[np.where(data['total_amount'].isna())[0]].apply(lambda i: i.date()),
        ignore_index=True)

    data['passenger_count'] = data['passenger_count'].apply(to_int)
    missing_date = missing_date.append(
        data['lpep_pickup_datetime'].iloc[np.where(data['passenger_count'].isna())[0]].apply(lambda i: i.date()),
        ignore_index=True)

    data = data.dropna(subset=['lpep_dropoff_datetime',
                               'passenger_count',
                               'trip_distance',
                               'total_amount'])
    valid_dates = data['lpep_pickup_datetime'].apply(lambda i: i.date())
    missing_date = pd.DataFrame(missing_date.apply(lambda s: None if s in valid_dates.values else s).dropna(),
                                columns=['missing_dates'])

    return missing_date


def usage_stat(path=None):
    data, _ = read_value_data(path)
    data.columns = np.vectorize(lambda s: s.lower())(data.columns)

    data['lpep_dropoff_datetime'] = data['lpep_dropoff_datetime'].apply(to_datetime)
    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].apply(to_datetime)
    data['trip_distance'] = data['trip_distance'].apply(to_float)
    data['passenger_count'] = data['passenger_count'].apply(to_int)
    data = data.dropna(subset=['lpep_pickup_datetime',
                               'lpep_dropoff_datetime',
                               'passenger_count',
                               'trip_distance',
                               'total_amount'])

    stat = data.groupby(data['lpep_pickup_datetime'].dt.date)['vendorid'].count()
    stat = pd.DataFrame(stat)
    stat.index.name = 'date'
    stat.columns = ['count']
    return stat


def trip_stat(path):
    data, _ = read_value_data(path)
    data.columns = np.vectorize(lambda s: s.lower())(data.columns)

    data['lpep_dropoff_datetime'] = data['lpep_dropoff_datetime'].apply(to_datetime)
    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].apply(to_datetime)
    data['trip_distance'] = data['trip_distance'].apply(to_float)
    data['passenger_count'] = data['passenger_count'].apply(to_int)
    data = data.dropna(subset=['lpep_pickup_datetime',
                               'lpep_dropoff_datetime',
                               'passenger_count',
                               'trip_distance',
                               'total_amount'])

    data['month'] = data['lpep_pickup_datetime'].apply(lambda d: d.month)

    if data['lpep_pickup_datetime'].shape[0] != 0:
        trip_stat = pd.DataFrame(data.groupby(['month', 'passenger_count'])['trip_distance'].mean())
    else:
        trip_stat = pd.DataFrame(data.groupby(['month', 'passenger_count'])['trip_distance'].count())

    return trip_stat