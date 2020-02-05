def read_csv(path):
    data = []
    with open(path, 'r') as f:
        for line in f:
            data.append(line[:-1].split(','))
    return data[0], data[1:]


def write_to_csv(filename, data, columns=None, sep=','):
    if type(data) == dict:
        with open(filename, 'w') as f:
            if columns is not None:
                f.write(sep.join(columns) + '\n')
            for key in data.keys():
                f.write(str(key) + sep + str(data[key]) + '\n')
    else:
        print('Unknown data type')