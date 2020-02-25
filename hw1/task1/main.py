import sys
import glob
import get_stats as stat
import averaging as avrg
import pandas as pd
import multiprocessing


def calc(path):
    data = stat.read_value_data(path)
    general_stat = stat.general_stats(data)
    missing_dates = stat.missing_dates(data, return_min_max=True, return_valid=True)
    usage_stat = stat.usage_stat(data)
    trip_stat = stat.trip_stat(data, return_count=True)
    return general_stat, missing_dates, usage_stat, trip_stat


def many_files(paths):
    if len(paths) == 0:
        raise FileExistsError('There is no files')

    general_stats = pd.DataFrame(columns=['mean_cost',
                                          'longest_ride',
                                          'max_count',
                                          'max_count_start',
                                          'max_count_end',
                                          'invalid_rows'])
    missing_stats = pd.DataFrame(columns=['missing_dates', 'min', 'max'])
    usage_stats = pd.DataFrame(columns=['count'])
    trip_stats = pd.DataFrame(columns=['trip_duration'])
    results = []

    def collect_result(result):
        results.append(result)

    p = multiprocessing.Pool(processes=4)
    for path in paths:
        async_res = p.map_async(calc, [path])
        results.append(async_res)
    p.close()
    p.join()

    for result in results:
        result = result.get()
        general_stat, missing_dates, usage_stat, trip_stat = result[0]
        general_stats = general_stats.append(general_stat, sort=False)
        missing_stats = missing_stats.append(missing_dates, sort=False)
        usage_stats = usage_stats.append(usage_stat, sort=False)
        trip_stats = trip_stats.append(trip_stat, sort=False)

    avrg.average_gen(general_stats).to_csv('./stats/gen_stat.csv', index=False)
    avrg.average_missing(missing_stats).to_csv('./stats/missing_dates.csv', index=False)
    avrg.average_usage(usage_stats).to_csv('./stats/usage_stat.csv')
    avrg.average_trip(trip_stats).to_csv('./stats/trip_stat.csv', header=True)


def _main():
    if sys.argv[1] == '-dir':
        if sys.argv[2][-1] == '/':
            csv_paths = glob.glob(sys.argv[2] + '*.csv')
        else:
            csv_paths = glob.glob(sys.argv[2] + '/' + '*.csv')
    else:
        csv_paths = sys.argv[1:]

    many_files(csv_paths)


if __name__ == '__main__':
    _main()
