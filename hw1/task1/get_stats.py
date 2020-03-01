import pandas as pd
import numpy as np
from pandas.errors import EmptyDataError


def read_value_data(path):
    try:
        header = pd.read_csv(path, nrows=0)

    except EmptyDataError as error:
        raise EmptyDataError('Empty file') from error

    try:
        data_without_header = pd.read_csv(path, skiprows=1, header=None)
    except EmptyDataError as error:
        raise EmptyDataError("There's only header") from error

    data_len = data_without_header.shape[1]
    header_len = header.shape[1]

    if data_len > header_len:
        len_difference = data_len - header_len
        columns_to_drop = list(range(data_len)[-len_difference:])

        data = data_without_header.drop(columns_to_drop, axis=1)
    elif data_len < header_len:
        raise ValueError(f"Header length is {header_len}, but data length is {data_len}.")
    else:
        data = data_without_header.copy()

    data.columns = header.columns
    data.columns = np.char.lower(np.array(data.columns, dtype=str))

    required_columns = ['lpep_pickup_datetime',
                        'lpep_dropoff_datetime',
                        'passenger_count',
                        'trip_distance',
                        'total_amount']

    data['lpep_pickup_datetime'] = data['lpep_pickup_datetime'].apply(convert_type(np.datetime64))
    data['lpep_dropoff_datetime'] = data['lpep_dropoff_datetime'].apply(convert_type(np.datetime64))
    data['trip_distance'] = data['trip_distance'].apply(convert_type(float))
    data['total_amount'] = data['total_amount'].apply(convert_type(float))
    data['passenger_count'] = data['passenger_count'].apply(convert_type(int))

    return data[required_columns]


def general_stats(data, return_count=True):
    gen_stat = {}
    invalid_rows = np.any(data.isna(), axis=1).sum()
    clean_data = data.dropna().copy()
    clean_data['trip_duration'] = trip_durations(clean_data['lpep_pickup_datetime'],
                                                 clean_data['lpep_dropoff_datetime'])
    invalid_rows += clean_data['trip_duration'].isna().sum()
    gen_stat['invalid_rows'] = invalid_rows
    clean_data = clean_data.dropna()

    datetime_durations = pd.to_timedelta(clean_data['trip_duration'], unit='s')
    trip_duration = datetime_durations.apply(format_timedelta)
    clean_data.loc[:, 'trip_duration'] = trip_duration

    longest = format_timedelta(clean_data['trip_duration'].max())

    gen_stat['longest_ride'] = longest
    gen_stat['mean_cost'] = clean_data['total_amount'].mean()

    pickup_times = pd.DataFrame(clean_data['lpep_pickup_datetime'])
    count_info = trip_count_info(pickup_times)
    gen_stat['max_count'] = count_info['max_count']
    gen_stat['max_count_start'] = count_info['max_count_start']
    gen_stat['max_count_end'] = count_info['max_count_end']

    if return_count:
        gen_stat['count'] = clean_data.shape[0]
    gen_stat = pd.DataFrame(gen_stat, index=[0])
    return gen_stat


def trip_count_info(pickup_times):
    return_stat = {}
    if len(pickup_times) != 0:
        pickup_times = pickup_times.reindex(pickup_times['lpep_pickup_datetime'])
        resampled_data = pickup_times['lpep_pickup_datetime'].resample('10T')
        ten_minutes_resample = resampled_data.count()

        max_count_start = ten_minutes_resample.idxmax()
        max_count = ten_minutes_resample.max()
        max_count_end = max_count_start + np.timedelta64(10, 'm')

        return_stat['max_count'] = max_count
        return_stat['max_count_start'] = max_count_start
        return_stat['max_count_end'] = max_count_end
    else:
        return_stat['max_count'] = None
        return_stat['max_count_start'] = None
        return_stat['max_count_end'] = None

    return return_stat


def missing_dates(data, return_min_max=False, return_valid=False):
    clean_data = data.dropna().copy()

    max_time = clean_data['lpep_pickup_datetime'].max()
    min_time = clean_data['lpep_pickup_datetime'].min()

    if max_time is pd.NaT or min_time is pd.NaT:
        date_range = None
    else:
        date_range = pd.date_range(min_time, max_time, freq='D').date
    missing_date = pd.Series(date_range)
    missing_date.name = 'missing_date'

    valid_dates = clean_data['lpep_pickup_datetime'].dt.date


    if return_valid:
        missing_date.name = 'valid_dates'
        missing_date = pd.DataFrame(missing_date.loc[np.logical_not(missing_date.isin(valid_dates))])
    else:
        missing_date = pd.DataFrame(missing_date.loc[missing_date.isin(valid_dates)])

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
    clean_data = data.dropna().copy()
    stat = clean_data.groupby(clean_data['lpep_pickup_datetime'].dt.date)['lpep_pickup_datetime'].count()
    stat = pd.DataFrame(stat)
    stat.index.name = 'date'
    stat.columns = ['count']
    return stat


def trip_stat(data, return_count=False):
    clean_data = data.dropna().copy()
    clean_data['trip_duration'] = trip_durations(clean_data['lpep_pickup_datetime'],
                                                 clean_data['lpep_dropoff_datetime'])

    clean_data.loc[:, 'passenger_count'] = clean_data['passenger_count'].astype(int)
    clean_data.loc[:, 'month'] = clean_data['lpep_pickup_datetime'].dt.month
    clean_data = clean_data.dropna()

    if len(clean_data['lpep_pickup_datetime']) != 0:
        trip_stats = pd.DataFrame(clean_data.groupby(['month', 'passenger_count'])['trip_duration'].mean())
        trip_stats.loc[:, 'trip_duration'] = pd.to_timedelta(trip_stats['trip_duration'].astype(int),
                                                            unit='s').apply(format_timedelta)
        if return_count:
            trip_stats['count'] = clean_data.groupby(['month', 'passenger_count'])['trip_duration'].count()
    else:
        trip_stats = pd.DataFrame(columns=['month', 'passenger_count', 'trip_duration'])

    return trip_stats


def trip_durations(start, end):
    trip_duration = end - start
    trip_duration = trip_duration.dt.total_seconds().copy()
    invalid_dates_indexes = trip_duration < 0
    trip_duration.loc[invalid_dates_indexes] = None
    return trip_duration


def convert_type(type_to_convert, return_if_exception=None):
    def return_function(x):
        try:
            x = type_to_convert(x)
        except Exception:
            return return_if_exception
        return x
    return return_function


def format_timedelta(datetime):
    day_index = 0
    datetime_str = str(datetime).split()
    if datetime_str[day_index] == '0':
        return datetime_str[-1]
    else:
        return str(datetime)
