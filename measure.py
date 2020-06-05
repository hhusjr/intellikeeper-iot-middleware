import numpy as np


def get_distance(rssi):
    a = 52
    n = 3.5
    return 10 ** ((rssi - a) / (10 * n))


def get_axis(measured_distances):
    print(measured_distances)
    n = len(measured_distances)

    mat_x = np.empty((n - 1, 2))
    mat_y = np.empty((n - 1, ))

    xn, yn, dn = measured_distances[n - 1]

    for i in range(n - 1):
        mat_x[i][0] = xn - measured_distances[i][0]
        mat_x[i][1] = yn - measured_distances[i][1]

    for i in range(n - 1):
        xx, yy, dd = measured_distances[i]
        mat_y[i] = (dd ** 2 - xx ** 2 - yy ** 2 - dn ** 2 + xn ** 2 + yn ** 2) / 2

    result = np.squeeze(np.mat(mat_x.T.dot(mat_x)).I.dot(mat_x.T).dot(mat_y.T).T)
    return list(result.tolist())[0]
