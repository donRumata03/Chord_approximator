import numpy as np


def delete_rubbish(spectrum, percent_edge = 0.001, logariphmate = True, to_cut = True):
    max_val = max(np.array(spectrum).T[0])
    edge = percent_edge * max_val
    for index, p in enumerate(spectrum):
        if p[1] < edge:
            spectrum[index] = (p[0], 0)

    if logariphmate:
        for index, p in enumerate(spectrum):
            if p[0] != 0:
                spectrum[index] = (np.log(p[0]), p[1])
            else:
                spectrum[index] = (-100, p[1])

    if to_cut:
        first_index = None
        last_index = None

        for i in range(len(spectrum)):
            if spectrum[i][1] != 0:
                first_index = i
                break

        for i in range(len(spectrum) - 1, -1, -1):
            if spectrum[i][1] != 0:
                last_index = i + 1
                break


        return spectrum[first_index:last_index]

    return spectrum


def zero_split(data : list): # Of tuples (x, y)
    res = []

    for i in range(len(data)):
        if (i == 0 and data[0][1] != 0) or (data[i - 1][1] == 0 and data[i][1] != 0):
            res.append([])
        if data[i][1] != 0:
            res[-1].append(data[i])

    return res

def test_splitter():
    test = [
        (0, 1),
        (1, 2),
        (2, 1),
        (3, 0),
        (4, 0),
        (5, 2),
        (6, 0),
        (7, 9),
        (8, 0)
    ]
    return zero_split(test)


if __name__ == "__main__":
    print(test_splitter())