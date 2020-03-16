import math
import sys
import statistics
from my_math import unique_count, unique_mean, index_by_value
from files import read_csv, write_to_csv


def _main():
    data = read_csv(sys.argv[1])
    users = [d[3] for d in data]
    prices = [float(d[2]) for d in data]
    stores = [d[1] for d in data]
    items = [d[0] for d in data]

    print(f'Unique value of stores: {len(set(stores))}')
    print(f'Unique value of items: {len(set(items))}')

    unique_users = unique_count(users)
    print(f'User with max price count: {max(unique_users, key=unique_users.get)}')

    print(f'~~~Amount of items in each store~~~')
    stores_count = unique_count(stores)
    for store in stores_count.keys():
        print(f'Store {store}: {stores_count[store]}')

    csv_name = 'mean_prices.csv'

    write_to_csv(csv_name, unique_mean(items, prices), columns=['ited_id', 'mean_price'])
    print(f"Mean prices was writen to {csv_name}")

    indexes = index_by_value(prices, max(prices))
    for index in indexes:
        print(f'Max price is {prices[index]} for item {items[index]} in store {stores[index]}')

    indexes = index_by_value(prices, min(prices))
    for index in indexes:
        print(f'Min price is {prices[index]} for item {items[index]} in store {stores[index]}')


if __name__ == '__main__':
    _main()
