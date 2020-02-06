import pandas as pd
import numpy as np


def average_gen(general_stats, rows_amount):
    mean_cost = 0
    data_len = 0
    longest_ride = np.timedelta64(0, 's')
    max_count = 0
    max_count_start = None
    max_count_end = None
    invalid_rows = 0

    for num in range(len(general_stats)):
        mean_cost += general_stats[num]['mean_cost'][0] * rows_amount[num]
        data_len += rows_amount[num]

        if longest_ride < np.timedelta64(general_stats[num]['longest_ride'][0]):
            longest_ride = general_stats[num]['longest_ride'][0]

        if max_count < general_stats[num]['max_count'][0]:
            max_count = general_stats[num]['max_count'][0]
            max_count_start = general_stats[num]['max_count_start'][0]
            max_count_end = general_stats[num]['max_count_end'][0]

        invalid_rows += general_stats[num]['invalid_rows'][0]

    avg_stat = {'mean_cost': mean_cost / data_len,
                'longest_ride': longest_ride,
                'max_count': max_count,
                'max_count_start': max_count_start,
                'max_count_end': max_count_end,
                'invalid_rows': invalid_rows}

    avg_stat = pd.DataFrame(avg_stat, index=[0])
    avg_stat.to_csv('./stats/gen_stat.csv')

    return avg_stat


def average_missing(missing_stats):
    misses = pd.Series([])
    for miss in missing_stats:
        misses = misses.append(miss['missing_dates'], ignore_index=True)
    misses.dropna()
    misses = pd.DataFrame({'missing_dates': misses})
    misses.to_csv('./stats/missing_dates.csv')
    return misses


def average_trip(trip_stats):
    df = pd.DataFrame({'date': [],
                       'average_passenger': [],
                       'mean_trip_duration': []})

    for trip in trip_stats:
        for line, date in zip(trip.values, trip.index):
            date = str(date[0]) + '.' + str(date[1])
            if date not in df['date']:
                df = df.append(pd.DataFrame({'date': date,
                                             'average_passenger': line[0],
                                             'mean_trip_duration': line[1],
                                             'count': line[2]},
                                            index=[date]),
                               ignore_index=True, sort=False)
            else:
                avg_count = line[1] + df[df['date'] == date]['count']
                mean_trip = (line[1]*line + df[df['date'] == date]['mean_trip_duration'] * df[df['date'] == date]['count'])
                df = df.append(pd.DataFrame({'date': date,
                                             'average_passenger': df[df['date'] == date]['average_passenger'] + line[0],
                                             'mean_trip_duration': mean_trip / avg_count,
                                             'count': line[2] + df[df['date'] == date]['count']},
                                            index=[date]),
                               ignore_index=True, sort=False)

    df.drop(columns=['count']).sort_values(by=['date']).to_csv('./stats/trip_stat.csv', index=False)
    return df


def average_usage(usage_stats):
    average = {}
    for usage in usage_stats:
        for index in usage.index:
            if index not in average.keys():
                average[index] = int(usage[usage.index == index]['count'])
            else:
                average[index] = int(average[index]) + int(usage[usage.index == index]['count'])
    avg_usage = []
    for key in average.keys():
        avg_usage.append([key, average[key]])
    avg_usage = pd.DataFrame(avg_usage, columns=['date', 'count']).sort_values(by='date')
    avg_usage.to_csv('./stats/usage_stat.csv', index=False)
    return avg_usage
