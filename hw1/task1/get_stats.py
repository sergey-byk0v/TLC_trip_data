import pandas as pd
import numpy as np


def general_stats(path):
    gen_stat = {}
    data = pd.read_csv(path)
    gen_stat['mean_cost'] = data['Total_amount'].mean()
    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].astype(np.datetime64)
    data['Lpep_dropoff_datetime'] = data['Lpep_dropoff_datetime'].astype(np.datetime64)
    data['trip_duration'] = data['Lpep_dropoff_datetime'] - data['lpep_pickup_datetime']
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

    missing_data_indices = np.append(np.where(data['Passenger_count'] == 0),
                                     np.unique(np.append(np.where(data['Pickup_longitude'] == 0),
                                               np.where(data['Dropoff_longitude'] == 0))))
    invalid_rows = missing_data_indices.shape
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

    missing_data_indices = np.append(np.where(data['Passenger_count'] == 0),
                                     np.unique(np.append(np.where(data['Pickup_longitude'] == 0),
                                               np.where(data['Dropoff_longitude'] == 0))))
    missing_dates = pd.DataFrame(data['Lpep_dropoff_datetime'][missing_data_indices])
    missing_dates.columns = ['missing_dates']
    return missing_dates, data


def usage_stat(path=None, data=None):
    if data is None and path is not None:
        data = pd.read_csv(path)
    elif path is None and data is not None:
        data = data
    else:
        return None
    invalid_indices = np.logical_or(data['Pickup_longitude'] == 0, data['Dropoff_longitude'] == 0)
    data['Lpep_dropoff_datetime'] = pd.to_datetime(data['Lpep_dropoff_datetime'])
    valid_indices = np.logical_not(invalid_indices)
    stat = data[np.logical_not(invalid_indices)].groupby(data['Lpep_dropoff_datetime'].dt.date)['VendorID'].count()
    stat.index.name = 'date'
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
    person_count = data['Passenger_count']
    person_count.index = data['Lpep_dropoff_datetime'].astype(np.datetime64)
    trip_stat = pd.DataFrame(person_count.resample('M').sum())
    trip_duration = data['Passenger_count']
    trip_duration.index = data['Lpep_dropoff_datetime'].astype(np.datetime64)
    trip_stat['trip_duration'] = trip_duration.resample('M').mean()
    trip_stat.index.name = 'date'
    trip_stat.columns = ['average_passenger', 'mean_trip_duration']
    return trip_stat, data
