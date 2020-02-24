import pandas as pd
import numpy as np
import csv


def convert_type(type_to_convert, return_if_exception=None):
    def return_function(x):
        try:
            x = type_to_convert(x)
        except Exception:
            return return_if_exception
        return x
    return return_function


def get_time(datetime):
    day_index = 0
    datetime_str = str(datetime).split()
    if datetime_str[day_index] == '0':
        return datetime_str[-1]
    else:
        return str(datetime)


def valid_duration(duration):
    if duration < 0:
        return None
    else:
        return duration


def read_value_data(path):
    data = []
    with open(path) as csv_file:
        reader = csv.reader(csv_file)
        header = reader.__next__()
        header_len = len(header)
        for row in reader:
            data.append(row[:header_len])

    data = pd.DataFrame(data, columns=header)
    data.columns = np.char.lower(np.array(data.columns, dtype=str))

    required_columns = ['lpep_pickup_datetime',
                        'lpep_dropoff_datetime',
                        'passenger_count',
                        'trip_distance',
                        'total_amount',
                        'trip_duration']

    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].apply(convert_type(np.datetime64))
    data['lpep_dropoff_datetime'] = data['lpep_dropoff_datetime'].apply(convert_type(np.datetime64))
    data['trip_duration'] = data['lpep_dropoff_datetime'] - data['lpep_pickup_datetime']
    data['trip_duration'] = data['trip_duration'].dt.total_seconds()
    data['trip_duration'] = data['trip_duration'].apply(valid_duration)
    data['trip_distance'] = data['trip_distance'].apply(convert_type(float))
    data['total_amount'] = data['total_amount'].apply(convert_type(float))
    data['passenger_count'] = data['passenger_count'].apply(convert_type(int))

    return data[required_columns]


def general_stats(data, return_count=True):
    gen_stat = {}
    invalid_rows = np.any(data.isna(), axis=1).sum()
    clean_data = data.dropna()
    gen_stat['mean_cost'] = clean_data['total_amount'].mean()
    clean_data['trip_duration'] = pd.to_timedelta(clean_data['trip_duration'], unit='s').apply(get_time)
    longest = get_time(clean_data['trip_duration'].max())
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

    if return_count:
        gen_stat['count'] = clean_data.shape[0]
    gen_stat = pd.DataFrame(gen_stat, index=[0])

    return gen_stat


def missing_dates(data, return_min_max=False, return_valid=False):
    clean_data = data.dropna()

    max_time = clean_data['lpep_pickup_datetime'].max()
    min_time = clean_data['lpep_pickup_datetime'].min()

    missing_date = pd.Series(pd.date_range(min_time, max_time, freq='D').date)
    missing_date.name = 'missing_dates'

    valid_dates = clean_data['lpep_pickup_datetime'].apply(lambda i: i.date())

    if return_valid:
        missing_date.name = 'valid_dates'
        missing_date = pd.DataFrame(missing_date.apply(lambda s: s if s in valid_dates.values else None).dropna())
    else:
        missing_date = pd.DataFrame(missing_date.apply(lambda s: None if s in valid_dates.values else s).dropna())

    if return_min_max:
        if len(missing_date) != 0:
            missing_date['min'] = None
            missing_date['min'].iloc[0] = min_time
            missing_date['max'] = None
            missing_date['max'].iloc[0] = max_time
        else:
            missing_date['min'] = None
            missing_date['max'] = None
            missing_date = missing_date.append({'missing_dates': None,
                                                'min': min_time,
                                                'max': max_time}, ignore_index=True)

    return missing_date


def usage_stat(data):
    clean_data = data.dropna()
    stat = clean_data.groupby(clean_data['lpep_pickup_datetime'].dt.date)['lpep_pickup_datetime'].count()
    stat = pd.DataFrame(stat)
    stat.index.name = 'date'
    stat.columns = ['count']

    return stat


def trip_stat(data, return_count=False):
    clean_data = data.dropna()
    clean_data['passenger_count'] = clean_data['passenger_count'].astype(int)
    clean_data['month'] = clean_data['lpep_pickup_datetime'].apply(lambda d: d.month)

    if len(clean_data['lpep_pickup_datetime']) != 0:
        trip_stats = pd.DataFrame(clean_data.groupby(['month', 'passenger_count'])['trip_duration'].mean())
        trip_stats['trip_duration'] = pd.to_timedelta(trip_stats['trip_duration'].apply(int), unit='s').apply(get_time)

        if return_count:
            trip_stats['count'] = clean_data.groupby(['month', 'passenger_count'])['trip_duration'].count()
    else:
        trip_stats = pd.DataFrame(['month', 'passenger_count', 'trip_duration'])

    return trip_stats
