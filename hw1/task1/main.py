import sys
import get_stats as stat


def _main():
    csv_path = sys.argv[1]
    stat.general_stats(csv_path).to_csv('./stats/gen_stat.csv', index=False)
    stat.missing_dates(path=csv_path).to_csv('./stats/missing_dates.csv', index=False)
    stat.usage_stat(csv_path).to_csv('./stats/usage_stat.csv')
    stat.trip_stat(csv_path).to_csv('./stats/trip_stat.csv')


if __name__ == '__main__':
    _main()
