from statistics import mean
from collections import defaultdict


def unique_count(data):
    counts = defaultdict(int)
    for value in data:
        counts[value] += 1

    return counts


def unique_mean(keys, values):
    means = defaultdict(list)

    for key, value in zip(keys, values):
        means[key].append(value)

    for key in means:
        means[key] = mean(means[key])

    return means


def index_by_value(data, value):
    indexes = [index for index in range(len(data)) if data[index] == value]
    return indexes
