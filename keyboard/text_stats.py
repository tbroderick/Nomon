import numpy as np

target = "isn't that the right thing to do "
response = "isn't that the right thing to do"


def r(x, y):
    return x != y


def calc_MSD(a, b):
    if a[-1] == " ":
        a = a[:-1]
    if b[-1] == " ":
        b = b[:-1]

    a = np.array(list(a))
    b = np.array(list(b))

    D = np.zeros((a.size, b.size))

    for i in range(a.size):
        D[i, 0] = i

    for j in range(b.size):
        D[0, j] = j

    for i in range(a.size):
        for j in range(b.size):
            D[i, j] = min(D[i-1, j]+1, D[i, j-1]+1, D[i-1, j-1] + r(a[i], b[j]))
    return D[-1, -1], D[-1, -1] / max(a.size, b.size)*100


MSD, error_rate = calc_MSD(np.array(list(target)), np.array(list(response)))


print("Min String Distance: ", MSD, "\nError Rate: ", error_rate)
