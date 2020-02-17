import pandas as pd
import numpy as np
import get_stats as stat


def average_gen(general_stats):
    avg_data = pd.DataFrame(columns=['mean_cost',
                                     'longest_ride',
                                     'max_count',
                                     'max_count_start',
                                     'max_count_end',
                                     'invalid_rows'])
    avg_data['mean_cost'] = [(general_stats['mean_cost'] * general_stats['count'] / general_stats['count'].sum()).sum()]
    avg_data['longest_ride'] = [general_stats['longest_ride'].max()]
    max_count_index = np.where(general_stats['max_count'] == general_stats['max_count'].max())[0][0]
    avg_data['max_count'] = general_stats['max_count'].iloc[max_count_index]
    avg_data['max_count_start'] = general_stats['max_count_start'].iloc[max_count_index]
    avg_data['max_count_end'] = general_stats['max_count_end'].iloc[max_count_index]
    avg_data['invalid_rows'] = general_stats['invalid_rows'].sum()

    return avg_data


def get_dates_outside(borders):
    min_index, max_index = 0, 1
    outside_dates = []
    current_max = borders.max()[0]
    for row in borders.sort_values(by=['min']).values:
        if current_max < row[min_index]:
            outside_dates.append(np.array(pd.date_range(current_max, row[min_index], freq='D')))
        current_max = row[max_index]

    outside_dates = np.array(outside_dates).flatten()
    return outside_dates


def average_missing(missing_stats):
    borders = missing_stats[['min', 'max']]
    borders = borders.dropna()
    outside_dates = get_dates_outside(borders)
    misses = pd.DataFrame(columns=['missing_dates'])
    misses['missing_dates'] = missing_stats['missing_dates']
    misses['missing_dates'] = misses['missing_dates'].append(pd.Series(outside_dates), ignore_index=True)
    misses = misses.dropna()
    misses['missing_dates'] = np.unique(misses['missing_dates'])

    return misses.dropna()


def average_usage(usage_stats):
    avg_data = pd.Series(name='count')
    avg_data = usage_stats.groupby(usage_stats.index).sum()
    avg_data.index.name = 'date'

    return pd.DataFrame(avg_data)


def average_trip(trip_stats):
    avg_data = pd.DataFrame(columns=['month',
                                     'passenger_count',
                                     'trip_duration'])
    if trip_stats.shape[0] == 0:
        return avg_data

    avg_data['trip_duration'] = pd.to_timedelta(trip_stats['trip_duration']).dt.total_seconds().values
    avg_data['month'] = pd.Series(trip_stats.index).apply(lambda i: i[0])
    avg_data['passenger_count'] = pd.Series(trip_stats.index).apply(lambda i: i[1])
    avg_data = avg_data.groupby(['month', 'passenger_count'])['trip_duration'].mean()
    avg_data = pd.to_timedelta(avg_data.apply(int), unit='s').apply(stat.get_time)
    return avg_data

