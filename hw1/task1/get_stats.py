import pandas as pd
import numpy as np


def convert_type_function(type_to_convert, return_if_exception=None):
    def return_function(x): 
        try:
            x = type_to_convert(x)
        except ValueError:
            return return_if_exception
        else:
            return x
    return return_function


def read_value_data(path):
    data = pd.read_csv(path, error_bad_lines=False)
    data.columns = np.char.lower(np.array(data.columns, dtype=str))

    data['lpep_dropoff_datetime'] = data['lpep_dropoff_datetime'].apply(convert_type_function(np.datetime64))
    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].apply(convert_type_function(np.datetime64))
    data['trip_distance'] = data['trip_distance'].apply(convert_type_function(float))
    data['total_amount'] = data['total_amount'].apply(convert_type_function(float))
    data['passenger_count'] = data['passenger_count'].apply(convert_type_function(int))
    return data


def general_stats(path=None, data=None):
    if data is None and path is not None:
        data = read_value_data(path)
    elif path is None and data is not None:
        data = data
    else:
        return None

    gen_stat = {}
    required_columns = ['lpep_pickup_datetime',
                        'lpep_dropoff_datetime',
                        'total_amount',
                        'passenger_count',
                        'trip_distance']

    invalid_rows = np.any(data[required_columns].isna(), axis=1).sum()

    clean_data = data[required_columns].dropna()

    gen_stat['mean_cost'] = clean_data['total_amount'].mean()
    clean_data['trip_duration'] = clean_data['lpep_dropoff_datetime'] - clean_data['lpep_pickup_datetime']
    longest = clean_data['trip_duration'].max()
    gen_stat['longest_ride'] = longest

    pickup_times = pd.DataFrame(clean_data['lpep_pickup_datetime'])
    if len(pickup_times) != 0:
        pickup_times.index = pickup_times['lpep_pickup_datetime']
        ten_minutes_resample = pickup_times['lpep_pickup_datetime'].resample('10T').count()
        max_count_start = ten_minutes_resample.idxmax()
        max_count = ten_minutes_resample.max()
        max_count_end = max_count_start + np.timedelta64(10, 'm')
        gen_stat['max_count'] = max_count
        gen_stat['max_count_start'] = max_count_start
        gen_stat['max_count_end'] = max_count_end

    gen_stat['invalid_rows'] = invalid_rows
    gen_stat['count'] = clean_data.shape[0]
    gen_stat = pd.DataFrame(gen_stat, index=[0])
    return gen_stat


def missing_dates(path=None, data=None):
    if data is None and path is not None:
        data = read_value_data(path)
    elif path is None and data is not None:
        data = data
    else:
        return None
    required_columns = ['lpep_pickup_datetime',
                        'lpep_dropoff_datetime',
                        'passenger_count',
                        'trip_distance',
                        'total_amount']

    clean_data = data[required_columns].dropna()
    max_time = clean_data['lpep_pickup_datetime'].max()
    min_time = clean_data['lpep_pickup_datetime'].min()
    missing_date = pd.Series(pd.date_range(min_time, max_time, freq='D').date)
    missing_date.name = 'missing_date'

    valid_dates = clean_data['lpep_pickup_datetime'].apply(lambda i: i.date())

    missing_date = pd.DataFrame(missing_date.apply(lambda s: None if s in valid_dates.values else s).dropna())
    return missing_date


def usage_stat(path=None, data=None):
    if data is None and path is not None:
        data = read_value_data(path)
    elif path is None and data is not None:
        data = data
    else:
        return None

    print(data.shape)
    required_columns = ['lpep_pickup_datetime',
                        'lpep_dropoff_datetime',
                        'total_amount',
                        'passenger_count',
                        'trip_distance']

    clean_data = data[required_columns].dropna()
    stat = clean_data.groupby(clean_data['lpep_pickup_datetime'].dt.date)['lpep_pickup_datetime'].count()
    stat = pd.DataFrame(stat)
    stat.index.name = 'date'
    stat.columns = ['count']
    return stat


def trip_stat(path=None, data=None):
    if data is None and path is not None:
        data = read_value_data(path)
    elif path is None and data is not None:
        data = data
    else:
        return None

    required_columns = ['lpep_pickup_datetime',
                        'lpep_dropoff_datetime',
                        'passenger_count',
                        'trip_distance',
                        'total_amount']

    clean_data = data[required_columns].dropna()
    clean_data['month'] = clean_data['lpep_pickup_datetime'].apply(lambda d: d.month)
    clean_data['trip_duration'] = clean_data['lpep_dropoff_datetime'] - clean_data['lpep_pickup_datetime']
    clean_data['trip_duration'] = clean_data['trip_duration'].dt.total_seconds()
    clean_data['trip_duration'] = clean_data['trip_duration'].apply(lambda d: None if d < 0 else d)
    clean_data = clean_data.dropna()

    if len(clean_data['lpep_pickup_datetime']) != 0:
        trip_stats = pd.DataFrame(clean_data.groupby(['month', 'passenger_count'])['trip_duration'].mean())
    else:
        trip_stats = pd.DataFrame(['month', 'passenger_count', 'trip_duration'])

    return trip_stats