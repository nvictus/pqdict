# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from itertools import combinations
import operator
import sys
import random

import pytest

from pqdict import pqdict, minpq, maxpq, nlargest, nsmallest


sample_keys = ["A", "B", "C", "D", "E", "F", "G"]
sample_values = [5, 8, 7, 3, 9, 12, 1]
sample_tuple_values = [
    ("a", 5), ("b", 8), (None, 7), (2.5, 3), ("e", 9), ("f", 12), ("g", 1)
]
sample_items = list(zip(sample_keys, sample_values))
sample_tuple_items = list(zip(sample_keys, sample_tuple_values))


def generate_data(value_type, num_items=None):
    # shuffled set of two-letter keys
    if num_items is None:
        pairs = combinations("ABCDEFGHIJKLMNOP", 2)  # 120 keys
        keys = ["".join(pair) for pair in pairs]
        random.shuffle(keys)
        num_items = len(keys)
    else:
        pairs = combinations("ABCDEFGHIJKLMNOP", 2)
        keys = ["".join(next(pairs)) for _ in range(num_items)]
        random.shuffle(keys)
    # different kinds of values
    if value_type == "int":
        values = [random.randint(0, 100) for i in range(num_items)]
    elif value_type == "float":
        values = [random.random() for i in range(num_items)]
    elif value_type == "unique":
        values = list(range(num_items))
        random.shuffle(values)
    return list(zip(keys, values))


def _check_heap_invariant(pq):
    heap = pq._heap
    for pos, node in enumerate(heap):
        if pos:  # pos 0 has no parent
            parentpos = (pos - 1) >> 1
            assert heap[parentpos].value <= node.value


def _check_index(pq):
    # All heap entries are pointed to by the index (_position)
    n = len(pq._heap)
    nodes = pq._position.values()
    assert list(range(n)) == sorted(nodes)
    # All heap entries map back to the correct dictionary key
    for key in pq._position:
        node = pq._heap[pq._position[key]]
        assert key == node.key


# The next group of tests were originally in class TestNew


def test_constructor():
    # sequence of pairs
    pq0 = pqdict(
        [("A", 5), ("B", 8), ("C", 7), ("D", 3), ("E", 9), ("F", 12), ("G", 1)]
    )
    pq1 = pqdict(zip(["A", "B", "C", "D", "E", "F", "G"], [5, 8, 7, 3, 9, 12, 1]))
    # dictionary
    pq2 = pqdict({"A": 5, "B": 8, "C": 7, "D": 3, "E": 9, "F": 12, "G": 1})
    # keyword arguments
    pq3 = minpq(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
    assert pq0 == pq1 == pq2 == pq3


def test_equality():
    # eq
    pq1 = pqdict(sample_items)
    pq2 = pqdict(sample_items)
    assert pq1 == pq2
    assert not pq1 != pq2
    # ne
    pq2[random.choice(sample_keys)] += 1
    assert not pq1 == pq2
    assert pq1 != pq2
    # pqdict == regular dict if they have same key/value pairs
    adict = dict(sample_items)
    assert pq1 == adict
    # TODO: FIX?
    # pqdicts evaluate as equal even if they have different
    # key functions and/or precedence functions
    pq3 = maxpq(sample_items)
    assert pq1 == pq3


def test_minpq():
    pq = minpq(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
    assert list(pq.popvalues()) == [1, 3, 5, 7, 8, 9, 12]
    assert pq.precedes == operator.lt


def test_maxpq():
    pq = maxpq(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
    assert list(pq.popvalues()) == [12, 9, 8, 7, 5, 3, 1]
    assert pq.precedes == operator.gt


def test_fromkeys():
    # assign same value to all
    seq = ["foo", "bar", "baz"]

    pq = pqdict.fromkeys(seq, 10)
    for k in seq:
        assert pq[k] == 10

    pq = pqdict.fromkeys(seq, float("inf"))
    for k in seq:
        assert pq[k] == float("inf")
    pq["spam"] = 10
    assert pq.pop() == "spam"

    pq = pqdict.fromkeys(seq, float("-inf"), precedes=operator.gt)
    for k in seq:
        assert pq[k] == float("-inf")
    pq["spam"] = 10
    assert pq.pop() == "spam"


# The next group of tests were originally in class TestDictAPI


def test_len():
    pq = pqdict()
    assert len(pq) == 0
    pq = pqdict(sample_items)
    assert len(pq) == len(sample_items)


def test_contains():
    pq = pqdict(sample_items)
    for key in sample_keys:
        assert key in pq


def test_getitem():
    pq = pqdict(sample_items)
    for key, value in sample_items:
        assert pq[key] == value


def test_setitem():
    n = len(sample_items)
    pq = pqdict(sample_items)
    pq["new"] = 1.0  # add
    assert pq["new"] == 1.0
    assert len(pq) == n + 1
    pq["new"] = 10.0  # update
    assert pq["new"] == 10.0
    assert len(pq) == n + 1


def test_delitem():
    n = len(sample_items)
    pq = pqdict(sample_items)
    key = random.choice(sample_keys)
    del pq[key]
    assert len(pq) == n - 1
    assert key not in pq
    with pytest.raises(KeyError):
        pq.pop(key)


def test_copy():
    pq1 = pqdict(sample_items)
    pq2 = pq1.copy()
    assert pq1 == pq2
    key = random.choice(sample_keys)
    pq2[key] += 1
    assert pq1[key] != pq2[key]
    assert pq1 != pq2


# inherited implementations
def test_get():
    pq = pqdict(sample_items)
    assert pq.get("A") == 5
    assert pq.get("A", None) == 5
    assert pq.get("does_not_exist", None) is None
    assert pq.get('does_not_exist') is None


def test_clear():
    pq = pqdict(sample_items)
    pq.clear()
    assert len(pq) == 0
    _check_index(pq)


def test_setdefault():
    pq = pqdict(sample_items)
    assert pq.setdefault("A", 99) == 5
    assert pq.setdefault("new", 99) == 99
    assert pq["new"] == 99


def test_update():
    pq1 = pqdict(sample_items)
    pq2 = pqdict()
    pq2["C"] = 3000
    pq2["D"] = 4000
    pq2["XYZ"] = 9000
    pq1.update(pq2)
    assert pq1["C"] == 3000
    assert pq1["D"] == 4000
    assert "XYZ" in pq1
    assert pq1["XYZ"] == 9000


def test_iter():
    # non-destructive
    n = len(sample_items)
    pq = pqdict(sample_items)
    for val in iter(pq):
        assert val in sample_keys
    assert len(list(iter(pq))) == len(sample_keys)
    assert len(pq) == n


def test_keys():
    pq = pqdict(sample_items)
    assert sorted(sample_keys) == sorted(pq.keys())
    assert sorted(sample_values) == [pq[key] for key in pq.copy().popkeys()]


def test_values():
    pq = pqdict(sample_items)
    assert sorted(sample_values) == sorted(pq.values())
    assert sorted(sample_values) == list(pq.popvalues())


def test_items():
    pq = pqdict(sample_items)
    assert sorted(sample_items) == sorted(pq.items())
    assert sorted(sample_values) == [item[1] for item in pq.popitems()]


# The next group of tests were originally inclass TestPQAPI
def test_keyfn():
    pq = pqdict()
    assert pq.keyfn(5) == 5
    pq = pqdict(key=lambda x: len(x))
    assert pq.keyfn([1, 2, 3]) == 3


def test_precedes():
    pq = pqdict()
    assert pq.precedes == operator.lt
    pq = pqdict(reverse=True)
    assert pq.precedes == operator.gt
    func = lambda x, y: len(x) < len(y)
    pq = pqdict(precedes=func)
    pq["a"] = ()
    pq["b"] = (1,)
    pq["c"] = (1, 2)
    pq["d"] = (1, 2, 3)
    assert list(pq.popvalues()) == [(), (1,), (1, 2), (1, 2, 3)]


def test_pop():
    # pop selected item - return value
    pq = minpq(A=5, B=8, C=1)
    value = pq.pop("B")
    assert value == 8
    pq.pop("A")
    pq.pop("C")
    with pytest.raises(KeyError):
        pq.pop("A")
    with pytest.raises(KeyError):
        pq.pop("does_not_exist")
    # no args and empty - throws
    with pytest.raises(KeyError):
        pq.pop()  # pq is now empty
    # no args - return top key
    pq = minpq(A=5, B=8, C=1)
    assert pq.pop() == "C"


def test_top():
    # empty
    pq = pqdict()
    with pytest.raises(KeyError):
        pq.top()
    # non-empty
    for num_items in range(1, 30):
        items = generate_data("float", num_items)
        pq = pqdict(items)
        assert pq.top() == min(items, key=lambda x: x[1])[0]


def test_popitem():
    pq = minpq(A=5, B=8, C=1)
    # pop top item
    key, value = pq.popitem()
    assert key == "C"
    assert value == 1


def test_topitem():
    # empty
    pq = pqdict()
    with pytest.raises(KeyError):
        pq.top()
    # non-empty
    for num_items in range(1, 30):
        items = generate_data("float", num_items)
        pq = pqdict(items)
        assert pq.topitem() == min(items, key=lambda x: x[1])


def test_additem():
    pq = pqdict(sample_items)
    pq.additem("new", 8.0)
    assert pq["new"] == 8.0
    with pytest.raises(KeyError):
        pq.additem("new", 1.5)


def test_updateitem():
    pq = pqdict(sample_items)
    key, value = random.choice(sample_items)
    # assign same value
    pq.updateitem(key, value)
    assert pq[key] == value
    # assign new value
    pq.updateitem(key, value + 1.0)
    assert pq[key] == value + 1.0
    # can only update existing keys
    with pytest.raises(KeyError):
        pq.updateitem("does_not_exist", 99.0)


def test_pushpopitem():
    pq = minpq(A=5, B=8, C=1)
    assert pq.pushpopitem("D", 10) == ("C", 1)
    assert pq.pushpopitem("E", 5) == ("E", 5)
    with pytest.raises(KeyError):
        pq.pushpopitem("A", 99)


def test_replace_key():
    pq = minpq(A=5, B=8, C=1)
    pq.replace_key("A", "Alice")
    pq.replace_key("B", "Bob")
    _check_index(pq)
    assert pq["Alice"] == 5
    assert pq["Bob"] == 8
    with pytest.raises(KeyError):
        pq.__getitem__("A")
    with pytest.raises(KeyError):
        pq.__getitem__("B")
    with pytest.raises(KeyError):
        pq.replace_key("C", "Bob")


def test_swap_priority():
    pq = minpq(A=5, B=8, C=1)
    pq.swap_priority("A", "C")
    _check_index(pq)
    assert pq["A"] == 1
    assert pq["C"] == 5
    assert pq.top() == "A"
    with pytest.raises(KeyError):
        pq.swap_priority("A", "Z")


def test_destructive_iteration():
    for trial in range(100):
        size = random.randrange(1, 50)
        items = generate_data("float", size)
        keys, values = zip(*items)
        if trial & 1:  # Half of the time, heapify using the constructor
            pq = pqdict(items)
        else:  # The rest of the time, insert items sequentially
            pq = pqdict()
            for key, value in items:
                pq[key] = value
        # NOTE: heapsort is NOT a stable sorting method, so keys with equal
        # priority keys are not guaranteed to have the same order as in the
        # original sequence.
        values_heapsorted = list(pq.popvalues())
        assert values_heapsorted == sorted(values)


# The next group of tests were originally in class TestOperations


@pytest.mark.skipif("sys.version_info <= (3,0)")
def test_uncomparable():
    # non-comparable priority keys (Python 3 only)
    # Python 3 has stricter comparison than Python 2
    pq = pqdict()
    pq.additem("a", [])
    with pytest.raises(TypeError):
        pq.additem("b", 5)


def test_heapify():
    for size in range(30):
        items = generate_data("int", size)
        pq = pqdict(items)
        _check_heap_invariant(pq)
        assert len(pq._heap) == size
        _check_index(pq)


def test_heapsort():
    # sequences of operations
    pq = pqdict()
    _check_heap_invariant(pq)
    _check_index(pq)
    # push in a sequence of items
    items = generate_data("int")
    added_items = []
    for key, value in items:
        pq.additem(key, value)
        _check_heap_invariant(pq)
        _check_index(pq)
        added_items.append((key, value))
    # pop out all the items
    popped_items = []
    while pq:
        key_value = pq.popitem()
        _check_heap_invariant(pq)
        _check_index(pq)
        popped_items.append(key_value)
    assert len(pq._heap) == 0
    _check_index(pq)


def test_updates():
    items = generate_data("int")
    keys, values = zip(*items)
    pq = pqdict(items)
    for _ in range(100):
        pq[random.choice(keys)] = random.randrange(25)
        _check_heap_invariant(pq)
        _check_index(pq)


def test_updates_and_deletes():
    items = generate_data("int")
    keys, values = zip(*items)
    pq = pqdict(items)
    for oper in range(100):
        if oper & 1:  # update random item
            key = random.choice(keys)
            p_new = random.randrange(25)
            pq[key] = p_new
            assert pq[key] == p_new
        elif pq:  # delete random item
            key = random.choice(list(pq.keys()))
            del pq[key]
            assert key not in pq
        _check_heap_invariant(pq)
        _check_index(pq)


def test_edgecases():
    keys = ["A", "B", "C", "D", "E", "F", "G"]
    values = [1, 1, 1, 1, 1, 1, 1]
    pq = pqdict(zip(keys, values))
    pq["B"] = 2
    _check_heap_invariant(pq)
    pq = pqdict(zip(keys, values))
    pq["B"] = 0
    _check_heap_invariant(pq)


def test_infvalue():
    keys = ["A", "B", "C", "D", "E", "F", "G"]
    values = [1, 2, 3, 4, 5, 6, 7]
    pq = pqdict(zip(keys, values))
    pq.additem("top", -float("inf"))
    pq.additem("bot", float("inf"))
    keys_sorted = [key for key in pq.popkeys()]
    assert keys_sorted[0] == "top"
    assert keys_sorted[-1] == "bot"


def test_datetime():
    pq = pqdict()
    dt = datetime.now()
    pq["a"] = dt
    pq["b"] = dt + timedelta(days=5)
    pq["c"] = dt + timedelta(seconds=5)
    assert list(pq.popkeys()) == ["a", "c", "b"]


def test_repair():
    mutable_value = [3]
    pq = minpq(A=[1], B=[2], C=mutable_value)
    assert pq[pq.top()] == [1]
    mutable_value[0] = 0
    assert pq[pq.top()] == [1]
    pq.heapify("C")
    assert pq[pq.top()] == [0]


# The next test was originally in class TestModuleFunctions
def test_nbest():
    top3 = nlargest(3, dict(sample_items))
    assert list(top3) == ["F", "E", "B"]
    bot3 = nsmallest(3, dict(sample_items))
    assert list(bot3) == ["G", "D", "A"]


def test_nbest_key():
    if sys.version_info.major > 2:
        with pytest.raises(TypeError):
            nlargest(3, dict(sample_tuple_items))
        with pytest.raises(TypeError):
            nsmallest(3, dict(sample_tuple_items))

    top3 = nlargest(3, dict(sample_tuple_items), key=operator.itemgetter(1))
    assert list(top3) == ["F", "E", "B"]
    bot3 = nsmallest(3, dict(sample_tuple_items), key=operator.itemgetter(1))
    assert list(bot3) == ["G", "D", "A"]
