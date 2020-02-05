from statistics import mean


def unique_count(data):
    counts = {}
    for value in data:
        if value not in counts.keys():
            counts[value] = 1
        else:
            counts[value] += 1

    return counts


def unique_mean(keys, values):
    means = {}
    for num in range(len(keys)):
        if keys[num] not in means.keys():
            means[keys[num]] = [values[num]]
        else:
            means[keys[num]].append(values[num])

    for key in means:
        means[key] = mean(means[key])

    return means


def index_by_value(data, value):
    indexes = []
    for index in range(len(data)):
        if data[index] == value:
            indexes.append(index)
    return indexes
