import pandas as pd
import sys
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
        mean_cost += general_stats[num]['mean_cost'][0] / rows_amount[num]
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
                'max_count_statr': max_count_start,
                'max_count_end': max_count_end,
                'invalid_rows': invalid_rows}

    avg_stat = pd.DataFrame(avg_stat, index=[0])
    avg_stat.to_csv('gen_stat.csv')

    return avg_stat


def average_missing(missing_stats):
    pass


def average_trip(trip_stats):
    pass


def average_usage(usage_stats):
    pass