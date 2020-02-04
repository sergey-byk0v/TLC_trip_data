import sys
import glob
import subprocess
import get_stats as stat
import averaging as avrg
import multiprocessing


def calc(path):
    try:
        general_stat, data = stat.general_stats(path)
    except ValueError as v:
        if subprocess.call(['sed', '-i', "'s/,,,//'", path]) == 0:
            general_stat, data = stat.general_stats(path)
        else:
            raise v
    missing_dates, _ = stat.missing_dates(data=data)
    usage_stat, _ = stat.usage_stat(data=data)
    trip_stat, _ = stat.trip_stat(data=data)

    return data.shape[0], general_stat, missing_dates, usage_stat, trip_stat


def many_files(paths):
    if len(paths) == 0:
        raise FileExistsError('There is no files')

    general_stats = []
    missing_stats = []
    usage_stats = []
    trip_stats = []
    rows_amount = []
    results = []

    p = multiprocessing.Pool(processes=4)
    for path in paths:
        async_res = p.map_async(calc, [path])
        results.append(async_res)
    p.close()
    p.join()
    for result in results:
        result = result.get()
        data_len, general_stat, missing_dates, usage_stat, trip_stat = result[0]
        rows_amount.append(data_len)
        general_stats.append(general_stat)
        missing_stats.append(missing_dates)
        usage_stats.append(usage_stat)
        trip_stats.append(trip_stat)

    avrg.average_gen(general_stats, rows_amount)
    avrg.average_missing(missing_stats)
    avrg.average_usage(usage_stats)
    avrg.average_trip(trip_stats)

    
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
