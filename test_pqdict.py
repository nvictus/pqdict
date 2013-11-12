#!/usr/bin/env python
from pqdict import PQDict
from itertools import combinations
import sys, random
import unittest

def generateData(pkey_type, num_items=None):
    # shuffled set of two-letter dictionary keys
    if num_items is None:
        pairs = combinations('ABCDEFGHIJKLMNOP', 2) #120 keys
        dkeys = [''.join(pair) for pair in pairs]
        random.shuffle(dkeys)
        num_items = len(dkeys)
    else:
        pairs = combinations('ABCDEFGHIJKLMNOP', 2)
        dkeys = [''.join(next(pairs)) for _ in range(num_items)]
        random.shuffle(dkeys)
        
    # different sets of priority keys
    if pkey_type == 'int':
        pkeys = [random.randint(0,100) for i in range(num_items)]
    elif pkey_type == 'float':
        pkeys = [random.random() for i in range(num_items)]
    elif pkey_type == 'unique':
        pkeys = list(range(num_items))
        random.shuffle(pkeys) 
    return list(zip(dkeys, pkeys))


class TestPQDict(unittest.TestCase):
    def check_heap_invariant(self, pq):
        heap = pq._heap
        for pos, entry in enumerate(heap):
            if pos: # pos 0 has no parent
                parentpos = (pos-1) >> 1
                self.assertLessEqual(heap[parentpos].pkey, entry.pkey)

    def check_index(self, pq):
        # All heap entries are pointed to by the index (nodefinder)
        n = len(pq._heap)
        nodes = pq._position.values()
        self.assertEqual(list(range(n)), sorted(nodes))
        # All heap entries map back to the correct dictionary key
        for dkey in pq._position:
            entry = pq._heap[pq._position[dkey]]
            self.assertEqual(dkey, entry.dkey)

class TestAPI(TestPQDict):
    def setUp(self):
        self.dkeys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        self.pkeys = [5, 8, 7, 3, 9, 12, 1]
        self.items = list(zip(self.dkeys, self.pkeys))

    def test_constructor(self):
        # sequence of pairs
        pq0 = PQDict([('A',5), ('B',8), ('C',7), ('D',3), ('E',9), ('F',12), ('G',1)])
        pq1 = PQDict(zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], [5, 8, 7, 3, 9, 12, 1]))
        # dictionary
        pq2 = PQDict({'A':5, 'B':8, 'C':7, 'D':3, 'E':9, 'F':12, 'G':1})
        # keyword arguments
        pq3 = PQDict(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
        self.assertTrue(pq0==pq1==pq2==pq3)

    def test_equality(self):
        # eq, ne
        pq1 = PQDict(self.items)
        pq2 = PQDict(self.items)
        self.assertTrue(pq1 == pq2)
        self.assertFalse(pq1 != pq2)

        pq2[random.choice(self.dkeys)] += 1
        self.assertTrue(pq1 != pq2)
        self.assertFalse(pq1 == pq2)

        # PQDict == regular dict should be legal and True if they have same key/value pairs
        adict = dict(self.items)
        self.assertEqual(pq1, adict)

        # False for seq of dkeys though
        self.assertNotEqual(pq1, self.dkeys)

    def test_inequalities(self):
        pass

    def test_len(self):
        pq = PQDict()
        self.assertEqual(len(pq), 0)
        pq = PQDict(self.items)
        self.assertEqual(len(pq), len(self.items))

    def test_contains(self):
        pq = PQDict(self.items)
        for dkey in self.dkeys:
            self.assertIn(dkey, pq)

    def test_getitem(self):
        pq = PQDict(self.items)
        for dkey, pkey in self.items:
            self.assertEqual(pq[dkey], pkey)

    def test_setitem(self):
        n = len(self.items)
        pq = PQDict(self.items)
        pq['new'] = 1.0 #add
        self.assertEqual(pq['new'], 1.0)
        self.assertEqual(len(pq), n+1)
        pq['new'] = 10.0 #update
        self.assertEqual(pq['new'], 10.0)
        self.assertEqual(len(pq), n+1) 

    def test_additem(self):
        pq = PQDict(self.items)
        pq.additem('new', 8.0)
        self.assertEqual(pq['new'], 8.0)
        self.assertRaises(KeyError, pq.additem, 'new', 1.5)

    def test_updateitem(self):
        pq = PQDict(self.items)
        dkey, pkey = random.choice(self.items)
        # assign same value
        pq.updateitem(dkey, pkey)
        self.assertEqual(pq[dkey], pkey)
        # assign new value
        pq.updateitem(dkey, pkey + 1.0)
        self.assertEqual(pq[dkey], pkey + 1.0)
        # can only update existing dkeys
        self.assertRaises(KeyError, pq.updateitem, 'does_not_exist', 99.0)  

    def test_delitem(self):
        n = len(self.items)
        pq = PQDict(self.items)
        dkey = random.choice(self.dkeys)
        del pq[dkey]
        self.assertEqual(len(pq), n-1)
        self.assertNotIn(dkey, pq)
        self.assertRaises(KeyError, pq.pop, dkey)

    def test_popitem(self):
        pq = PQDict(A=5, B=8, C=1)
        # pop top item
        dkey, pkey = pq.popitem()
        self.assertEqual(dkey,'C') and self.assertEqual(pkey,1)

    def test_pop(self):
        # pop selected item - return pkey
        pq = PQDict(A=5, B=8, C=1)
        pkey = pq.pop('B')
        self.assertEqual(pkey, 8)
        pq.pop('A')
        pq.pop('C')
        self.assertRaises(KeyError, pq.pop, 'A')
        self.assertRaises(KeyError, pq.pop, 'does_not_exist')
        self.assertRaises(KeyError, pq.popitem) #pq is now empty

    def test_iter(self):
        # non-destructive
        n = len(self.items)
        pq = PQDict(self.items)
        for val in iter(pq):
            self.assertIn(val, self.dkeys)
        self.assertEqual(len(list(iter(pq))), len(self.dkeys))
        self.assertEqual(len(pq), n)

    def test_copy(self):
        pq1 = PQDict(self.items)
        pq2 = pq1.copy()
        # equality by value
        self.assertEqual(pq1, pq2)

        dkey = random.choice(self.dkeys)
        pq2[dkey] += 1  
        self.assertNotEqual(pq1[dkey], pq2[dkey])
        self.assertNotEqual(pq1, pq2)

    def test_peek(self):
        # empty
        pq = PQDict()
        self.assertRaises(KeyError, pq.peek)
        # non-empty
        for num_items in range(1,30):
            items = generateData('float', num_items)
            pq = PQDict(items)
            self.assertTrue(pq.peek() == min(items, key=lambda x: x[1]))


    # inherited methods
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
        self.check_index(pq)

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
        self.assertEqual(pq1['C'],3000) and \
        self.assertEqual(pq1['D'],4000) and \
        self.assertIn('XYZ',pq1) and \
        self.assertEqual(pq1['XYZ'],9000)

    def test_keys(self):
        # the "keys" are dictionary keys
        pq = PQDict(self.items)
        self.assertEqual(sorted(self.dkeys), sorted(pq.keys()))
        self.assertEqual(sorted(self.pkeys), [pq[dkey] for dkey in pq.copy().iterkeys()])


    def test_values(self):
        # the "values" are priority keys
        pq = PQDict(self.items)   
        self.assertEqual(sorted(self.pkeys), sorted(pq.values()))
        self.assertEqual(sorted(self.pkeys), list(pq.itervalues()))

    def test_items(self):
        pq = PQDict(self.items)
        self.assertEqual(sorted(self.items), sorted(pq.items()))
        self.assertEqual(sorted(self.pkeys), [item[1] for item in pq.iteritems()])

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
            self.check_heap_invariant(pq)
            self.assertTrue(len(pq._heap)==size)
            self.check_index(pq)

    def test_insert_pop(self):
        # sequences of operations
        pq = PQDict()
        self.check_heap_invariant(pq)
        self.check_index(pq)

        items = generateData('int')

        # push in a sequence of items
        added_items = []
        for dkey, pkey in items:
            pq.additem(dkey, pkey)
            self.check_heap_invariant(pq)
            self.check_index(pq)
            added_items.append( (dkey,pkey) )

        # pop out all the items
        popped_items = []
        while pq:
            dkey_pkey = pq.popitem()
            self.check_heap_invariant(pq)
            self.check_index(pq)
            popped_items.append(dkey_pkey)

        self.assertTrue(len(pq._heap)==0)
        self.check_index(pq)

    def test_update(self):
        pq = PQDict()
        items = generateData('int')
        dkeys, pkeys = zip(*items)
        pq = PQDict(items)
        for _ in range(100):
            pq[random.choice(dkeys)] = random.randrange(25)
            self.check_heap_invariant(pq)
            self.check_index(pq)

    def test_update_remove(self):
        pq = PQDict()

        items = generateData('int')
        dkeys, pkeys = zip(*items)

        # heapify a sequence of items
        pq = PQDict(items)

        for oper in range(100):
            if oper & 1: #update random item
                dkey = random.choice(dkeys)
                p_new = random.randrange(25)
                pq[dkey] = p_new
                self.assertTrue(pq[dkey]==p_new)
            elif pq: #delete random item
                dkey = random.choice(list(pq.keys()))
                del pq[dkey]
                self.assertTrue(dkey not in pq)
            self.check_heap_invariant(pq)
            self.check_index(pq)

    def test_heapsort(self):
        for trial in range(100):
            size = random.randrange(1,50)
            items = generateData('float', size)
            dkeys, pkeys = zip(*items)

            if trial & 1:     # Half of the time, heapify using the constructor
                pq = PQDict(items)
            else:             # The rest of the time, insert items sequentially
                pq = PQDict()
                for dkey, pkey in items:
                   pq[dkey] = pkey

            # NOTE: heapsort is NOT a stable sorting method, so dkeys with equal priority keys
            # are not guaranteed to have the same order as in the original sequence.
            pkeys_heapsorted = [pq.popitem()[1] for i in range(size)]
            self.assertEqual(pkeys_heapsorted, sorted(pkeys))

    def test_edgecases(self):
        dkeys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        pkeys = [1, 1, 1, 1, 1, 1, 1]
        pq = PQDict(zip(dkeys, pkeys))
        pq['B'] = 2
        self.check_heap_invariant(pq)

        dkeys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        pkeys = [1, 1, 1, 1, 1, 1, 1]
        pq = PQDict(zip(dkeys, pkeys))
        pq['B'] = 0
        self.check_heap_invariant(pq)

    def test_infpkey(self):
        dkeys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        pkeys = [1, 2, 3, 4, 5, 6, 7]
        pq = PQDict(zip(dkeys, pkeys))
        pq.additem('top', -float('inf'))
        pq.additem('bot', float('inf'))
        dkeys_sorted = [key for key in pq.iterkeys()]
        self.assertEqual(dkeys_sorted[0], 'top')
        self.assertEqual(dkeys_sorted[-1], 'bot')



if __name__ == '__main__':
    unittest.main()

