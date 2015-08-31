# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from itertools import combinations
from operator import itemgetter
import operator
import random
import sys

from pqdict import *
import unittest


def generateData(value_type, num_items=None):
    # shuffled set of two-letter dictionary keys
    if num_items is None:
        pairs = combinations('ABCDEFGHIJKLMNOP', 2)  # 120 keys
        keys = [''.join(pair) for pair in pairs]
        random.shuffle(keys)
        num_items = len(keys)
    else:
        pairs = combinations('ABCDEFGHIJKLMNOP', 2)
        keys = [''.join(next(pairs)) for _ in range(num_items)]
        random.shuffle(keys)
        
    # different sets of priority keys
    if value_type == 'int':
        value = [random.randint(0,100) for i in range(num_items)]
    elif value_type == 'float':
        value = [random.random() for i in range(num_items)]
    elif value_type == 'unique':
        value = list(range(num_items))
        random.shuffle(value)
    return list(zip(keys, value))


class TestPQDict(unittest.TestCase):
    def setUp(self):
        self.keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        self.values = [5, 8, 7, 3, 9, 12, 1]
        self.items = list(zip(self.keys, self.values))

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
        pq0 = PQDict([('A',5), ('B',8), ('C',7), ('D',3), ('E',9), ('F',12), ('G',1)])
        pq1 = PQDict(zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], [5, 8, 7, 3, 9, 12, 1]))
        # dictionary
        pq2 = PQDict({'A':5, 'B':8, 'C':7, 'D':3, 'E':9, 'F':12, 'G':1})
        # keyword arguments
        pq3 = minpq(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
        self.assertTrue(pq0==pq1==pq2==pq3)

    def test_equality(self):
        # eq
        pq1 = PQDict(self.items)
        pq2 = PQDict(self.items)
        self.assertTrue(pq1 == pq2)
        self.assertFalse(pq1 != pq2)
        # ne
        pq2[random.choice(self.keys)] += 1
        self.assertFalse(pq1 == pq2)
        self.assertTrue(pq1 != pq2)
        # PQDict == regular dict if they have same key/value pairs
        adict = dict(self.items)
        self.assertEqual(pq1, adict)
        # XXX: FIX? - PQDicts evaluate as equal even if they have different pq-types
        pq3 = maxpq(self.items)
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
        pq = PQDict.fromkeys(seq, float('inf'))
        for k in pq:
            self.assertEqual(pq[k], float('inf'))
        pq = PQDict.fromkeys(seq, 10)
        for k in pq:
            self.assertEqual(pq[k], 10)
        pq = PQDict.fromkeys(seq, float('-inf'), precedes=operator.gt)
        for k in pq:
            self.assertEqual(pq[k], float('-inf'))


class TestDictAPI(TestPQDict):

    def test_len(self):
        pq = PQDict()
        self.assertEqual(len(pq), 0)
        pq = PQDict(self.items)
        self.assertEqual(len(pq), len(self.items))

    def test_contains(self):
        pq = PQDict(self.items)
        for key in self.keys:
            self.assertIn(key, pq)

    def test_getitem(self):
        pq = PQDict(self.items)
        for key, value in self.items:
            self.assertEqual(pq[key], value)

    def test_setitem(self):
        n = len(self.items)
        pq = PQDict(self.items)
        pq['new'] = 1.0 #add
        self.assertEqual(pq['new'], 1.0)
        self.assertEqual(len(pq), n+1)
        pq['new'] = 10.0 #update
        self.assertEqual(pq['new'], 10.0)
        self.assertEqual(len(pq), n+1) 

    def test_delitem(self):
        n = len(self.items)
        pq = PQDict(self.items)
        key = random.choice(self.keys)
        del pq[key]
        self.assertEqual(len(pq), n-1)
        self.assertNotIn(key, pq)
        self.assertRaises(KeyError, pq.pop, key)

    def test_copy(self):
        pq1 = PQDict(self.items)
        pq2 = pq1.copy()
        # equality by value
        self.assertEqual(pq1, pq2)

        key = random.choice(self.keys)
        pq2[key] += 1  
        self.assertNotEqual(pq1[key], pq2[key])
        self.assertNotEqual(pq1, pq2)

    # inherited implementations
    def test_get(self):
        pq = PQDict(self.items)
        self.assertEqual(pq.get('A'), 5)
        self.assertEqual(pq.get('A', None), 5)
        self.assertIs(pq.get('does_not_exist', None), None)
        self.assertRaises(KeyError, pq.get('does_not_exist'))

    def test_clear(self):
        pq = PQDict(self.items)
        pq.clear()
        self.assertEqual(len(pq), 0)
        self._check_index(pq)

    def test_setdefault(self):
        pq = PQDict(self.items)
        self.assertEqual(pq.setdefault('A',99), 5)
        self.assertEqual(pq.setdefault('new',99), 99)
        self.assertEqual(pq['new'], 99)

    def test_update(self):
        pq1 = PQDict(self.items)
        pq2 = PQDict()
        pq2['C'] = 3000
        pq2['D'] = 4000
        pq2['XYZ'] = 9000
        pq1.update(pq2)
        self.assertEqual(pq1['C'],3000) 
        self.assertEqual(pq1['D'],4000)
        self.assertIn('XYZ',pq1)
        self.assertEqual(pq1['XYZ'],9000)

    # non-destructive iterators
    def test_iter(self):
        # non-destructive
        n = len(self.items)
        pq = PQDict(self.items)
        for val in iter(pq):
            self.assertIn(val, self.keys)
        self.assertEqual(len(list(iter(pq))), len(self.keys))
        self.assertEqual(len(pq), n)

    def test_keys(self):
        # the "keys" are dictionary keys
        pq = PQDict(self.items)
        self.assertEqual(sorted(self.keys), sorted(pq.keys()))
        self.assertEqual(sorted(self.values), [pq[key] for key in pq.copy().popkeys()])

    def test_values(self):
        # the "values" are priority keys
        pq = PQDict(self.items)   
        self.assertEqual(sorted(self.values), sorted(pq.values()))
        self.assertEqual(sorted(self.values), list(pq.popvalues()))

    def test_items(self):
        pq = PQDict(self.items)
        self.assertEqual(sorted(self.items), sorted(pq.items()))
        self.assertEqual(sorted(self.values), [item[1] for item in pq.popitems()])


class TestPQAPI(TestPQDict):

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
        self.assertRaises(KeyError, pq.pop) #pq is now empty
        # no args - return top key
        pq = minpq(A=5, B=8, C=1)
        self.assertEqual(pq.pop(), 'C')

    def test_top(self):
        # empty
        pq = PQDict()
        self.assertRaises(KeyError, pq.top)
        # non-empty
        for num_items in range(1,30):
            items = generateData('float', num_items)
            pq = PQDict(items)
            self.assertEqual(pq.top(), min(items, key=lambda x: x[1])[0])

    def test_popitem(self):
        pq = minpq(A=5, B=8, C=1)
        # pop top item
        key, value = pq.popitem()
        self.assertEqual(key,'C')
        self.assertEqual(value,1)

    def test_topitem(self):
        # empty
        pq = PQDict()
        self.assertRaises(KeyError, pq.top)
        # non-empty
        for num_items in range(1,30):
            items = generateData('float', num_items)
            pq = PQDict(items)
            self.assertEqual(pq.topitem(), min(items, key=lambda x: x[1]))

    def test_additem(self):
        pq = PQDict(self.items)
        pq.additem('new', 8.0)
        self.assertEqual(pq['new'], 8.0)
        self.assertRaises(KeyError, pq.additem, 'new', 1.5)

    def test_updateitem(self):
        pq = PQDict(self.items)
        key, value = random.choice(self.items)
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
            items = generateData('float', size)
            keys, values = zip(*items)

            if trial & 1:     # Half of the time, heapify using the constructor
                pq = PQDict(items)
            else:             # The rest of the time, insert items sequentially
                pq = PQDict()
                for key, value in items:
                   pq[key] = value

            # NOTE: heapsort is NOT a stable sorting method, so keys with equal priority keys
            # are not guaranteed to have the same order as in the original sequence.
            values_heapsorted = list(pq.popvalues())
            self.assertEqual(values_heapsorted, sorted(values))


class TestOperations(TestPQDict):

    @unittest.skipIf(sys.version_info[0] < 3, "only applies to Python 3")
    def test_uncomparable(self):
        # non-comparable priority keys (Python 3 only) 
        # Python 3 has stricter comparison than Python 2
        pq = PQDict()
        pq.additem('a',[])
        self.assertRaises(TypeError, pq.additem, 'b', 5)

    def test_heapify(self):
        for size in range(30):
            items = generateData('int', size)
            pq = PQDict(items)
            self._check_heap_invariant(pq)
            self.assertTrue(len(pq._heap)==size)
            self._check_index(pq)

    def test_heapsort(self):
        # sequences of operations
        pq = PQDict()
        self._check_heap_invariant(pq)
        self._check_index(pq)

        items = generateData('int')

        # push in a sequence of items
        added_items = []
        for key, value in items:
            pq.additem(key, value)
            self._check_heap_invariant(pq)
            self._check_index(pq)
            added_items.append( (key,value) )

        # pop out all the items
        popped_items = []
        while pq:
            key_value = pq.popitem()
            self._check_heap_invariant(pq)
            self._check_index(pq)
            popped_items.append(key_value)

        self.assertTrue(len(pq._heap)==0)
        self._check_index(pq)

    def test_updates(self):
        pq = PQDict()
        items = generateData('int')
        keys, values = zip(*items)
        pq = PQDict(items)
        for _ in range(100):
            pq[random.choice(keys)] = random.randrange(25)
            self._check_heap_invariant(pq)
            self._check_index(pq)

    def test_updates_and_deletes(self):
        pq = PQDict()

        items = generateData('int')
        keys, values = zip(*items)

        # heapify a sequence of items
        pq = PQDict(items)

        for oper in range(100):
            if oper & 1: #update random item
                key = random.choice(keys)
                p_new = random.randrange(25)
                pq[key] = p_new
                self.assertTrue(pq[key]==p_new)
            elif pq: #delete random item
                key = random.choice(list(pq.keys()))
                del pq[key]
                self.assertTrue(key not in pq)
            self._check_heap_invariant(pq)
            self._check_index(pq)

    def test_edgecases(self):
        keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        values = [1, 1, 1, 1, 1, 1, 1]
        pq = PQDict(zip(keys, values))
        pq['B'] = 2
        self._check_heap_invariant(pq)

        keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        values = [1, 1, 1, 1, 1, 1, 1]
        pq = PQDict(zip(keys, values))
        pq['B'] = 0
        self._check_heap_invariant(pq)

    def test_infvalue(self):
        keys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        values = [1, 2, 3, 4, 5, 6, 7]
        pq = PQDict(zip(keys, values))
        pq.additem('top', -float('inf'))
        pq.additem('bot', float('inf'))
        keys_sorted = [key for key in pq.popkeys()]
        self.assertEqual(keys_sorted[0], 'top')
        self.assertEqual(keys_sorted[-1], 'bot')

    def test_datetime(self):
        pq = PQDict()
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
        top3 = nlargest(3, dict(self.items))
        self.assertEqual(list(top3), ['F', 'E', 'B'])
        bot3 = nsmallest(3, dict(self.items))
        self.assertEqual(list(bot3), ['G', 'D', 'A'])


if __name__ == '__main__':
    unittest.main()

