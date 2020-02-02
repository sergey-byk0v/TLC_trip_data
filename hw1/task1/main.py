import pandas as pd
import sys
import numpy as np
import subprocess
import get_stats as stat
import averaging as avrg


def many_paths(paths):
    general_stats = []
    missing_stats = []
    usage_stats = []
    trip_stats = []
    rows_amount = []

    for path in paths:
        try:
            general_stat, data = stat.general_stats(path)
        except ValueError as v:
            if subprocess.call(['sed', '-i', "'s/,,,//'", path]) == 0:
                general_stat, data = stat.general_stats(path)
            else:
                raise v
        # missing_dates, _ = stat.missing_dates(data=data)
        # usage_stat, _ = stat.usage_stat(data=data)
        # trip_stat, _ = stat.trip_trip_stat(data=data)

        rows_amount.append(data.shape[0])
        general_stats.append(general_stat)
        # missing_stats.append(missing_dates)
        # usage_stats.append(usage_stats)
        # trip_stats.append(trip_stat)

    avrg.average_gen(general_stats, rows_amount)
    # avrg.average_missing(missing_stats)
    # avrg.average_usage(usage_stats)
    # avrg.average_trip(trip_stats)


def _main():
    csv_paths = sys.argv[1:]
    many_paths(csv_paths)


if __name__ == '__main__':
    _main()
