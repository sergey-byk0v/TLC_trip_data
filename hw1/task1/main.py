import sys
import get_stats as stat


def _main():
    csv_path = sys.argv[1]
    data = stat.read_value_data(csv_path)
    stat.general_stats(data=data).to_csv('./stats/gen_stat.csv', index=False)
    stat.missing_dates(data=data).to_csv('./stats/missing_dates.csv', index=False)
    stat.usage_stat(data=data).to_csv('./stats/usage_stat.csv')
    stat.trip_stat(data=data).to_csv('./stats/trip_stat.csv')


if __name__ == '__main__':
    _main()
