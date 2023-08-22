import numpy as np
import matplotlib.pyplot as plt



def offset_failure(data, offset):
    return data + offset


def drifting_failure(data, factor):
    modified_data = []

    for i in range(np.shape(data)[0]):
        modified_data.append(data[i] + factor * i)

    return np.asarray(modified_data)


def precision_degradation(data, min, max):
    modified_data = []

    for i in range(np.shape(data)[0]):
        random = np.random.uniform(min, max)
        modified_data.append(data[i] + random)

    return np.asarray(modified_data)


def total_failure(data, total_failure_value):
    return np.zeros(np.shape(data)) + total_failure_value

if __name__ == "__main__":
    test = np.expand_dims(np.arange(20, ), axis=1)
    test2 = np.expand_dims(np.arange(20, 40), axis=1)

    test = np.concatenate([test, test2], axis=-1)
    print(test, np.shape(test))

    offset_data = offset_failure(test, 10)
    print(offset_data, np.shape(offset_data))

    drifting_data = drifting_failure(test, 1)
    print(drifting_data, np.shape(drifting_data))

    deg_data = precision_degradation(test, -1, 1)
    print(deg_data, np.shape(deg_data))

    total_data = total_failure(test, 0)
    print(total_data, np.shape(total_data))

    # visualize data
    # initialize figure
    # fig = plt.figure(figsize=(20, 13))
    # ax = []
    x = np.arange(0, np.shape(test)[0])

    # ax.append(fig.add_subplot(3, 2, 1))
    # ax[-1].set_title("normal")
    # plt.plot(x, test)

    # ax.append(fig.add_subplot(3, 2, 2))
    # ax[-1].set_title("drifting")
    # plt.plot(x, drifting_data)

    # ax.append(fig.add_subplot(3, 2, 3))
    # ax[-1].set_title("degradation")
    # plt.plot(x, deg_data)

    # ax.append(fig.add_subplot(3, 2, 4))
    # ax[-1].set_title("total fail")
    # plt.plot(x, total_data)

    # ax.append(fig.add_subplot(3, 2, 5))
    # ax[-1].set_title("offset")
    # plt.plot(x, offset_data)

    # plt.show()

    plt.plot(x, test)
    plt.plot(x, drifting_data)
    plt.plot(x, deg_data)
    plt.plot(x, total_data)
    plt.plot(x, offset_data)
    plt.show()


