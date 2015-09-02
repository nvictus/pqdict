# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from itertools import combinations
import operator
import random
import sys
import unittest

from pqdict import pqdict, minpq, maxpq, nlargest, nsmallest


sample_keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
sample_values = [5, 8, 7, 3, 9, 12, 1]
sample_items = list(zip(sample_keys, sample_values))


def generate_data(value_type, num_items=None):
    # shuffled set of two-letter keys
    if num_items is None:
        pairs = combinations('ABCDEFGHIJKLMNOP', 2)  # 120 keys
        keys = [''.join(pair) for pair in pairs]
        random.shuffle(keys)
        num_items = len(keys)
    else:
        pairs = combinations('ABCDEFGHIJKLMNOP', 2)
        keys = [''.join(next(pairs)) for _ in range(num_items)]
        random.shuffle(keys)
    # different kinds of values
    if value_type == 'int':
        values = [random.randint(0, 100) for i in range(num_items)]
    elif value_type == 'float':
        values = [random.random() for i in range(num_items)]
    elif value_type == 'unique':
        values = list(range(num_items))
        random.shuffle(values)
    return list(zip(keys, values))


class TestPQDict(unittest.TestCase):
    def _check_heap_invariant(self, pq):
        heap = pq._heap
        for pos, node in enumerate(heap):
            if pos:  # pos 0 has no parent
                parentpos = (pos-1) >> 1
                self.assertLessEqual(heap[parentpos].value, node.value)

    def _check_index(self, pq):
        # All heap entries are pointed to by the index (_position)
        n = len(pq._heap)
        nodes = pq._position.values()
        self.assertEqual(list(range(n)), sorted(nodes))
        # All heap entries map back to the correct dictionary key
        for key in pq._position:
            node = pq._heap[pq._position[key]]
            self.assertEqual(key, node.key)


class TestNew(TestPQDict):

    def test_constructor(self):
        # sequence of pairs
        pq0 = pqdict(
            [('A',5), ('B',8), ('C',7), ('D',3), ('E',9), ('F',12), ('G',1)])
        pq1 = pqdict(
            zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], [5, 8, 7, 3, 9, 12, 1]))
        # dictionary
        pq2 = pqdict({'A': 5, 'B': 8, 'C': 7, 'D': 3, 'E': 9, 'F': 12, 'G': 1})
        # keyword arguments
        pq3 = minpq(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
        self.assertTrue(pq0 == pq1 == pq2 == pq3)

    def test_equality(self):
        # eq
        pq1 = pqdict(sample_items)
        pq2 = pqdict(sample_items)
        self.assertTrue(pq1 == pq2)
        self.assertFalse(pq1 != pq2)
        # ne
        pq2[random.choice(sample_keys)] += 1
        self.assertFalse(pq1 == pq2)
        self.assertTrue(pq1 != pq2)
        # pqdict == regular dict if they have same key/value pairs
        adict = dict(sample_items)
        self.assertEqual(pq1, adict)
        # TODO: FIX? 
        # pqdicts evaluate as equal even if they have different 
        # key functions and/or precedence functions
        pq3 = maxpq(sample_items)
        self.assertEqual(pq1, pq3)

    def test_minpq(self):
        pq = minpq(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
        self.assertEqual(
            list(pq.popvalues()), 
            [1, 3, 5, 7, 8, 9, 12])
        self.assertEqual(pq.precedes, operator.lt)

    def test_maxpq(self):
        pq = maxpq(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
        self.assertEqual(
            list(pq.popvalues()), 
            [12, 9, 8 ,7, 5, 3, 1])
        self.assertEqual(pq.precedes, operator.gt)

    def test_fromkeys(self):
        # assign same value to all
        seq = ['foo', 'bar', 'baz']

        pq = pqdict.fromkeys(seq, 10)
        for k in seq:
            self.assertEqual(pq[k], 10)
        
        pq = pqdict.fromkeys(seq, float('inf'))
        for k in seq:
            self.assertEqual(pq[k], float('inf'))
        pq['spam'] = 10
        self.assertEqual(pq.pop(), 'spam')

        pq = pqdict.fromkeys(seq, float('-inf'), precedes=operator.gt)
        for k in seq:
            self.assertEqual(pq[k], float('-inf'))
        pq['spam'] = 10
        self.assertEqual(pq.pop(), 'spam')


class TestDictAPI(TestPQDict):

    def test_len(self):
        pq = pqdict()
        self.assertEqual(len(pq), 0)
        pq = pqdict(sample_items)
        self.assertEqual(len(pq), len(sample_items))

    def test_contains(self):
        pq = pqdict(sample_items)
        for key in sample_keys:
            self.assertIn(key, pq)

    def test_getitem(self):
        pq = pqdict(sample_items)
        for key, value in sample_items:
            self.assertEqual(pq[key], value)

    def test_setitem(self):
        n = len(sample_items)
        pq = pqdict(sample_items)
        pq['new'] = 1.0  # add
        self.assertEqual(pq['new'], 1.0)
        self.assertEqual(len(pq), n+1)
        pq['new'] = 10.0  # update
        self.assertEqual(pq['new'], 10.0)
        self.assertEqual(len(pq), n+1) 

    def test_delitem(self):
        n = len(sample_items)
        pq = pqdict(sample_items)
        key = random.choice(sample_keys)
        del pq[key]
        self.assertEqual(len(pq), n-1)
        self.assertNotIn(key, pq)
        self.assertRaises(KeyError, pq.pop, key)

    def test_copy(self):
        pq1 = pqdict(sample_items)
        pq2 = pq1.copy()
        self.assertEqual(pq1, pq2)
        key = random.choice(sample_keys)
        pq2[key] += 1  
        self.assertNotEqual(pq1[key], pq2[key])
        self.assertNotEqual(pq1, pq2)

    # inherited implementations
    def test_get(self):
        pq = pqdict(sample_items)
        self.assertEqual(pq.get('A'), 5)
        self.assertEqual(pq.get('A', None), 5)
        self.assertIs(pq.get('does_not_exist', None), None)
        self.assertRaises(KeyError, pq.get('does_not_exist'))

    def test_clear(self):
        pq = pqdict(sample_items)
        pq.clear()
        self.assertEqual(len(pq), 0)
        self._check_index(pq)

    def test_setdefault(self):
        pq = pqdict(sample_items)
        self.assertEqual(pq.setdefault('A',99), 5)
        self.assertEqual(pq.setdefault('new',99), 99)
        self.assertEqual(pq['new'], 99)

    def test_update(self):
        pq1 = pqdict(sample_items)
        pq2 = pqdict()
        pq2['C'] = 3000
        pq2['D'] = 4000
        pq2['XYZ'] = 9000
        pq1.update(pq2)
        self.assertEqual(pq1['C'],3000) 
        self.assertEqual(pq1['D'],4000)
        self.assertIn('XYZ',pq1)
        self.assertEqual(pq1['XYZ'],9000)

    def test_iter(self):
        # non-destructive
        n = len(sample_items)
        pq = pqdict(sample_items)
        for val in iter(pq):
            self.assertIn(val, sample_keys)
        self.assertEqual(len(list(iter(pq))), len(sample_keys))
        self.assertEqual(len(pq), n)

    def test_keys(self):
        pq = pqdict(sample_items)
        self.assertEqual(sorted(sample_keys), sorted(pq.keys()))
        self.assertEqual(
            sorted(sample_values), [pq[key] for key in pq.copy().popkeys()])

    def test_values(self):
        pq = pqdict(sample_items)   
        self.assertEqual(sorted(sample_values), sorted(pq.values()))
        self.assertEqual(sorted(sample_values), list(pq.popvalues()))

    def test_items(self):
        pq = pqdict(sample_items)
        self.assertEqual(sorted(sample_items), sorted(pq.items()))
        self.assertEqual(
            sorted(sample_values), [item[1] for item in pq.popitems()])


class TestPQAPI(TestPQDict):

    def test_keyfn(self):
        pq = pqdict()
        self.assertEqual(pq.keyfn(5), 5)
        pq = pqdict(key=lambda x: len(x))
        self.assertEqual(pq.keyfn([1,2,3]), 3)

    def test_precedes(self):
        pq = pqdict()
        self.assertEqual(pq.precedes, operator.lt)
        pq = pqdict(reverse=True)
        self.assertEqual(pq.precedes, operator.gt)
        func = lambda x, y: len(x) < len(y)
        pq = pqdict(precedes=func)
        pq['a'] = ()
        pq['b'] = (1,)
        pq['c'] = (1,2)
        pq['d'] = (1,2,3)
        self.assertEqual(list(pq.popvalues()), [(), (1,), (1,2), (1,2,3)])

    def test_pop(self):
        # pop selected item - return value
        pq = minpq(A=5, B=8, C=1)
        value = pq.pop('B')
        self.assertEqual(value, 8)
        pq.pop('A')
        pq.pop('C')
        self.assertRaises(KeyError, pq.pop, 'A')
        self.assertRaises(KeyError, pq.pop, 'does_not_exist')
        # no args and empty - throws
        self.assertRaises(KeyError, pq.pop)  # pq is now empty
        # no args - return top key
        pq = minpq(A=5, B=8, C=1)
        self.assertEqual(pq.pop(), 'C')

    def test_top(self):
        # empty
        pq = pqdict()
        self.assertRaises(KeyError, pq.top)
        # non-empty
        for num_items in range(1,30):
            items = generate_data('float', num_items)
            pq = pqdict(items)
            self.assertEqual(pq.top(), min(items, key=lambda x: x[1])[0])

    def test_popitem(self):
        pq = minpq(A=5, B=8, C=1)
        # pop top item
        key, value = pq.popitem()
        self.assertEqual(key,'C')
        self.assertEqual(value,1)

    def test_topitem(self):
        # empty
        pq = pqdict()
        self.assertRaises(KeyError, pq.top)
        # non-empty
        for num_items in range(1,30):
            items = generate_data('float', num_items)
            pq = pqdict(items)
            self.assertEqual(pq.topitem(), min(items, key=lambda x: x[1]))

    def test_additem(self):
        pq = pqdict(sample_items)
        pq.additem('new', 8.0)
        self.assertEqual(pq['new'], 8.0)
        self.assertRaises(KeyError, pq.additem, 'new', 1.5)

    def test_updateitem(self):
        pq = pqdict(sample_items)
        key, value = random.choice(sample_items)
        # assign same value
        pq.updateitem(key, value)
        self.assertEqual(pq[key], value)
        # assign new value
        pq.updateitem(key, value + 1.0)
        self.assertEqual(pq[key], value + 1.0)
        # can only update existing keys
        self.assertRaises(KeyError, pq.updateitem, 'does_not_exist', 99.0)

    def test_pushpopitem(self):
        pq = minpq(A=5, B=8, C=1)
        self.assertEqual(pq.pushpopitem('D', 10), ('C', 1))
        self.assertEqual(pq.pushpopitem('E', 5), ('E', 5))
        self.assertRaises(KeyError, pq.pushpopitem, 'A', 99)

    def test_replace_key(self):
        pq = minpq(A=5, B=8, C=1)
        pq.replace_key('A', 'Alice')
        pq.replace_key('B', 'Bob')
        self._check_index(pq)
        self.assertEqual(pq['Alice'], 5)
        self.assertEqual(pq['Bob'], 8)
        self.assertRaises(KeyError, pq.__getitem__, 'A')
        self.assertRaises(KeyError, pq.__getitem__, 'B')
        self.assertRaises(KeyError, pq.replace_key, 'C', 'Bob')

    def test_swap_priority(self):
        pq = minpq(A=5, B=8, C=1)
        pq.swap_priority('A', 'C')
        self._check_index(pq)
        self.assertEqual(pq['A'], 1)
        self.assertEqual(pq['C'], 5)
        self.assertEqual(pq.top(), 'A')
        self.assertRaises(KeyError, pq.swap_priority, 'A', 'Z')

    def test_destructive_iteration(self):
        for trial in range(100):
            size = random.randrange(1,50)
            items = generate_data('float', size)
            keys, values = zip(*items)
            if trial & 1:     # Half of the time, heapify using the constructor
                pq = pqdict(items)
            else:             # The rest of the time, insert items sequentially
                pq = pqdict()
                for key, value in items:
                    pq[key] = value
            # NOTE: heapsort is NOT a stable sorting method, so keys with equal
            # priority keys are not guaranteed to have the same order as in the
            # original sequence.
            values_heapsorted = list(pq.popvalues())
            self.assertEqual(values_heapsorted, sorted(values))


class TestOperations(TestPQDict):

    @unittest.skipIf(sys.version_info[0] < 3, "only applies to Python 3")
    def test_uncomparable(self):
        # non-comparable priority keys (Python 3 only)
        # Python 3 has stricter comparison than Python 2
        pq = pqdict()
        pq.additem('a',[])
        self.assertRaises(TypeError, pq.additem, 'b', 5)

    def test_heapify(self):
        for size in range(30):
            items = generate_data('int', size)
            pq = pqdict(items)
            self._check_heap_invariant(pq)
            self.assertTrue(len(pq._heap) == size)
            self._check_index(pq)

    def test_heapsort(self):
        # sequences of operations
        pq = pqdict()
        self._check_heap_invariant(pq)
        self._check_index(pq)
        # push in a sequence of items
        items = generate_data('int')
        added_items = []
        for key, value in items:
            pq.additem(key, value)
            self._check_heap_invariant(pq)
            self._check_index(pq)
            added_items.append((key, value))
        # pop out all the items
        popped_items = []
        while pq:
            key_value = pq.popitem()
            self._check_heap_invariant(pq)
            self._check_index(pq)
            popped_items.append(key_value)
        self.assertTrue(len(pq._heap) == 0)
        self._check_index(pq)

    def test_updates(self):
        items = generate_data('int')
        keys, values = zip(*items)
        pq = pqdict(items)
        for _ in range(100):
            pq[random.choice(keys)] = random.randrange(25)
            self._check_heap_invariant(pq)
            self._check_index(pq)

    def test_updates_and_deletes(self):
        items = generate_data('int')
        keys, values = zip(*items)
        pq = pqdict(items)
        for oper in range(100):
            if oper & 1:  # update random item
                key = random.choice(keys)
                p_new = random.randrange(25)
                pq[key] = p_new
                self.assertTrue(pq[key] == p_new)
            elif pq:  # delete random item
                key = random.choice(list(pq.keys()))
                del pq[key]
                self.assertTrue(key not in pq)
            self._check_heap_invariant(pq)
            self._check_index(pq)

    def test_edgecases(self):
        keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        values = [1, 1, 1, 1, 1, 1, 1]
        pq = pqdict(zip(keys, values))
        pq['B'] = 2
        self._check_heap_invariant(pq)
        pq = pqdict(zip(keys, values))
        pq['B'] = 0
        self._check_heap_invariant(pq)

    def test_infvalue(self):
        keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        values = [1, 2, 3, 4, 5, 6, 7]
        pq = pqdict(zip(keys, values))
        pq.additem('top', -float('inf'))
        pq.additem('bot', float('inf'))
        keys_sorted = [key for key in pq.popkeys()]
        self.assertEqual(keys_sorted[0], 'top')
        self.assertEqual(keys_sorted[-1], 'bot')

    def test_datetime(self):
        pq = pqdict()
        dt = datetime.now()
        pq['a'] = dt
        pq['b'] = dt + timedelta(days=5)
        pq['c'] = dt + timedelta(seconds=5)
        self.assertEqual(list(pq.popkeys()), ['a', 'c', 'b'])

    def test_repair(self):
        mutable_value = [3]
        pq = minpq(A=[1], B=[2], C=mutable_value)
        self.assertEqual(pq[pq.top()], [1])
        mutable_value[0] = 0
        self.assertEqual(pq[pq.top()], [1])
        pq.heapify('C')
        self.assertEqual(pq[pq.top()], [0])


class TestModuleFunctions(TestPQDict):
    def test_nbest(self):
        top3 = nlargest(3, dict(sample_items))
        self.assertEqual(list(top3), ['F', 'E', 'B'])
        bot3 = nsmallest(3, dict(sample_items))
        self.assertEqual(list(bot3), ['G', 'D', 'A'])


if __name__ == '__main__':
    unittest.main()
