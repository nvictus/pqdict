import random
import timeit

import pqdict


def get_dict(n):
    a = pqdict.pqdict()
    for _ in range(n):
        a[random.random()] = random.random()
    return a


def update_dict(a):
    for key, value in a.items():
        a[key] = value + 0.001
    return a


def copy_dict(a):
    return a.copy()


def consume_dict(a):
    while a:
        assert a.popitem()[1]


if __name__ == "__main__":
    random.seed(1298472)

    a = get_dict(10_000)

    print("Time it takes to create the pqdict:")
    print(timeit.timeit(lambda: get_dict(1000), number=100))

    print("Time it takes to copy using pqdict.copy():")
    print(timeit.timeit(lambda: copy_dict(a), number=100))

    print("Time it takes to consume the pqdict after pqdict.copy():")
    print(timeit.timeit(lambda: consume_dict(copy_dict(a)), number=100))

    print("Time it takes to update all keys in the dict")
    print(timeit.timeit(lambda: update_dict(a), number=100))
