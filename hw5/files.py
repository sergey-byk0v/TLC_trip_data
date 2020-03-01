def read_csv(path):
    data = []
    with open(path, 'r') as f:
        for line in f:
            data.append(line[:-1].split(','))
    return data[1:]


def write_to_csv(filename, data, columns=None, sep=','):
    if isinstance(data, dict):
        with open(filename, 'w') as f:
            if columns is not None:
                f.write(sep.join(columns) + '\n')
            for key, value in data.items():
                f.write(str(key) + sep + str(value) + '\n')
    else:
        raise TypeError('Unknown data type')
