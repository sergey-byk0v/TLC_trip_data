import pandas as pd
import numpy as np


def general_stats(path):
    gen_stat = {}
    data = pd.read_csv(path)
    columns = []
    for column in data.columns:
        columns.append(column.lower())
    data.columns = columns
    gen_stat['mean_cost'] = data['total_amount'].mean()
    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].astype(np.datetime64)
    data['lpep_dropoff_datetime'] = data['lpep_dropoff_datetime'].astype(np.datetime64)
    data['trip_duration'] = data['lpep_dropoff_datetime'] - data['lpep_pickup_datetime']
    longest = data['trip_duration'].max()
    gen_stat['longest_ride'] = longest

    pickup_times = pd.DataFrame(data['lpep_pickup_datetime'])
    pickup_times.index = pickup_times['lpep_pickup_datetime']
    max_count_start = pickup_times['lpep_pickup_datetime'].resample('10T').count().idxmax()
    max_count = pickup_times['lpep_pickup_datetime'].resample('10T').count().max()
    max_count_end = max_count_start + np.timedelta64(10, 'm')
    gen_stat['max_count'] = max_count
    gen_stat['max_count_start'] = max_count_start
    gen_stat['max_count_end'] = max_count_end

    # invalid data where 0 passengers or 0 trip distance
    missing_data_indices = np.logical_or(data['passenger_count'] == 0, data['trip_distance'] == 0)
    invalid_rows = np.sum(missing_data_indices)
    gen_stat['invalid_rows'] = invalid_rows
    gen_stat = pd.DataFrame(gen_stat, index=[0])
    return gen_stat, data


def missing_dates(path=None, data=None):
    if data is None and path is not None:
        data = pd.read_csv(path)
    elif path is None and data is not None:
        data = data
    else:
        return None

    missing_data_indices = np.unique(np.append(np.where(data['passenger_count'] == 0),
                                               np.where(data['trip_distance'] == 0)))
    missing_dates = pd.DataFrame(np.array(data['lpep_dropoff_datetime'])[missing_data_indices])
    missing_dates.columns = ['missing_dates']
    return missing_dates, data


def usage_stat(path=None, data=None):
    if data is None and path is not None:
        data = pd.read_csv(path)
    elif path is None and data is not None:
        data = data
    else:
        return None
    invalid_indices = np.logical_or(data['passenger_count'] == 0, data['trip_distance'] == 0)
    data['lpep_dropoff_datetime'] = pd.to_datetime(data['lpep_dropoff_datetime'])
    valid_indices = np.logical_not(invalid_indices)
    stat = data[valid_indices].groupby(data['lpep_dropoff_datetime'].dt.date)['vendorid'].count()
    stat = pd.DataFrame(stat)
    stat.columns = ['count']
    return stat, data


def trip_stat(path=None, data=None):
    if data is None and path is not None:
        data = pd.read_csv(path)
    elif path is None and data is not None:
        data = data
    else:
        return None
    person_count = data['passenger_count']
    person_count.index = data['lpep_dropoff_datetime'].astype(np.datetime64)
    trip_stat = pd.DataFrame(person_count.groupby(by=[person_count.index.year, person_count.index.month]).sum())
    trip_duration = data['passenger_count']
    trip_duration.index = data['lpep_dropoff_datetime'].astype(np.datetime64)
    trip_stat['trip_duration'] = trip_duration.groupby(by=[trip_duration.index.year, trip_duration.index.month]).mean()
    trip_stat['count'] = trip_duration.groupby(by=[trip_duration.index.year, trip_duration.index.month]).count()
    trip_stat.index.name = 'date'
    trip_stat.columns = ['average_passenger', 'mean_trip_duration', 'count']

    return trip_stat, data
