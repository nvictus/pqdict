#!/usr/bin/env python

import pqdict
import random
from itertools import combinations
import unittest

class TestPQD(unittest.TestCase):
    def setUp(self):
        pairs = combinations('ABCDEFGHIJKLMNOP', 2)
        self.dkeys = [''.join(pair) for pair in pairs]; random.shuffle(self.dkeys)
        self.pkeys_float = [random.random() for i in range(len(self.dkeys))]
        self.pkeys_int = [random.randint(0,100) for i in range(len(self.dkeys))]
        self.pkeys_unique = list(range(len(self.dkeys))); random.shuffle(self.pkeys_unique)
        self.maxDiff = None

    #def tearDown(self)

    def check_heap_invariant(self, pq):
        heap = pq.heap
        for pos, entry in enumerate(heap):
            if pos: # pos 0 has no parent
                parentpos = (pos-1) >> 1
                self.assertTrue(heap[parentpos] <= entry)

    def check_index(self, pq):
        # All heap nodes are pointed to by the index (nodefinder)
        n = len(pq.heap)
        nodes = pq.nodefinder.values()
        self.assertTrue(list(range(n))==sorted(nodes))
        # All indexed items are referenced in their corresponding heap entry
        for dkey in pq.nodefinder.keys():
            entry = pq.heap[pq.nodefinder[dkey]]
            self.assertTrue(dkey == entry.key)

    def test_heapify(self):
        for size in range(30):
            dkeys = self.dkeys[:size]
            pkeys = self.pkeys_float[:size]
            pq = pqdict.PriorityQueueDict(zip(dkeys, pkeys))
            self.check_heap_invariant(pq)
            self.assertTrue(len(pq.heap)==size)
            self.check_index(pq)

    def test_equality(self):
        # eq, ne
        dkeys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        pkeys = [5, 8, 7, 3, 9, 12, 1]
        pq = pqdict.PriorityQueueDict(zip(dkeys, pkeys))
        pq2 = pqdict.PriorityQueueDict(zip(dkeys, pkeys))
        self.assertTrue(pq==pq2)
        self.assertFalse(pq!=pq2)
        pq2['B'] = 1000
        self.assertTrue(pq!=pq2)
        self.assertFalse(pq==pq2)
        # pqd == regular dict should be legal and True if they have same key/value pairs...
        self.assertTrue(pq==dict(zip(dkeys, pkeys)))
        # False for seq of items though
        self.assertFalse(pq==dkeys)

    def test_constructor(self):
        pq0 = pqdict.PriorityQueueDict([('A',5), ('B',8), ('C',7), ('D',3), ('E',9), ('F',12), ('G',1)])
        pq1 = pqdict.PriorityQueueDict(zip(['A', 'B', 'C', 'D', 'E', 'F', 'G'], [5, 8, 7, 3, 9, 12, 1]))
        pq2 = pqdict.PriorityQueueDict({'A':5, 'B':8, 'C':7, 'D':3, 'E':9, 'F':12, 'G':1})
        pq3 = pqdict.PriorityQueueDict(A=5, B=8, C=7, D=3, E=9, F=12, G=1)
        self.assertTrue(pq0==pq1==pq2==pq3)

    def test_copy(self):
        dkeys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        pkeys = [5, 8, 7, 3, 9, 12, 1]
        pq = pqdict.PriorityQueueDict(zip(dkeys, pkeys))
        pq2 = pq.copy()
        self.assertTrue(pq == pq2)
        pq2['A'] = 9000
        self.assertFalse(pq['A'] == pq2['A'])

    def test_api(self):
        pq = pqdict.PriorityQueueDict()
        self.assertTrue(len(pq)==0)

        # add new item:
        pq.add('a', 8.0)
        self.assertTrue(pq['a'] == 8.0)
        self.assertRaises(KeyError, pq.add, 'a', 1.5)

        # update item:
        pq.updateitem('a', 1.5)
        self.assertTrue(pq['a'] == 1.5)
        self.assertRaises(KeyError, pq.updateitem, 'fake', 99)

        # setitem
        pq['b'] = 1.0 #add
        self.assertTrue(pq['b']==1.0)
        pq['b'] = 10.0 #update
        self.assertTrue(pq['b']==10.0)

        # pop min item:
        item, pkey = pq.popitem()
        self.assertTrue(item=='a' and pkey==1.5)

        # pop selected item's pkey:
        pkey = pq.pop('b')
        self.assertTrue(pkey==10.0)
        self.assertRaises(KeyError, pq.popitem) #pq is empty
        self.assertRaises(KeyError, pq.pop, 'fake')

        del pq

        # peek at min item:
        pq = pqdict.PriorityQueueDict()
        self.assertRaises(KeyError, pq.peek)
        for size in range(1,30):
            dkeys = self.dkeys[:size]
            pkeys = self.pkeys_float[:size]
            data = list(zip(dkeys, pkeys))
            pq = pqdict.PriorityQueueDict(data)
            self.assertTrue(pq.peek() == min(data, key=lambda x: x[1]))

        del pq

        # inherited methods
        dkeys = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        pkeys = [5, 8, 7, 3, 9, 12, 1]
        pq = pqdict.PriorityQueueDict(zip(dkeys, pkeys))

        # get
        self.assertTrue(pq.get('A')==5)
        self.assertTrue(pq.get('A', None)==5)
        self.assertTrue(pq.get('X', None) is None)
        self.assertRaises(KeyError, pq.get('X'))

        # setdefault
        self.assertTrue(pq.setdefault('A',99)==5)
        self.assertTrue(pq.setdefault('X',99)==99)
        self.assertTrue(pq['X']==99)

        # clear
        pq.clear()
        self.assertTrue(len(pq)==0)
        self.check_index(pq)

        # update
        pq2 = pqdict.PriorityQueueDict()
        pq2['C'] = 3000
        pq2['D'] = 4000
        pq2['XYZ'] = 9000
        pq.update(pq2)
        assert(pq['C']==3000 and pq['D']==4000 and pq['XYZ']==9000)

    def test_insert_pop(self):
        pq = pqdict.PriorityQueueDict()
        self.check_heap_invariant(pq)
        self.check_index(pq)

        dkeys = self.dkeys
        pkeys = self.pkeys_int

        # push in a sequence of items
        data = []
        for dkey, pkey in zip(dkeys, pkeys):
            pq.add(dkey, pkey)
            self.check_heap_invariant(pq)
            self.check_index(pq)
            data.append( (dkey,pkey) )

        # pop out all the items
        results = []
        while pq:
            dkey_pkey = pq.popitem()
            self.check_heap_invariant(pq)
            self.check_index(pq)
            results.append(dkey_pkey)
        self.assertTrue(len(pq.heap)==0)
        self.check_index(pq)

        # incompatible priority keys
        pq.add('a',[])
        self.assertRaises(TypeError, pq.add, 'b', 5)

    def test_update_remove(self):
        pq = pqdict.PriorityQueueDict()

        dkeys = self.dkeys
        pkeys = self.pkeys_int

        # heapify a sequence of items
        pq = pqdict.PriorityQueueDict(zip(dkeys, pkeys))

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
            size = random.randrange(50)
            dkeys = self.dkeys[:size]
            pkeys = [random.randrange(25) for i in range(size)]
            data = zip(dkeys, pkeys)

            if trial & 1:     # Half of the time, use heapify
                pq = pqdict.PriorityQueueDict(data)
            else:             # The rest of the time, insert items sequentially
                pq = pqdict.PriorityQueueDict()
                for dkey,pkey in data:
                   pq[dkey] = pkey

            # NOTE: heapsort is NOT a stable sorting method, so items with equal priority keys
            # are not guaranteed to have the same order as in the original sequence.
            pairs_heapsorted = [pq.popitem() for i in range(size)]
            pkeys_heapsorted = [pair[1] for pair in pairs_heapsorted]
            self.assertEqual(pkeys_heapsorted, sorted(pkeys))








# we use a strict < comparison for bubbling the nodes around
# updating produces lufo ordering of equal keys
# last-in/updated-first-out. Note that popping/removing updates the bottom-most element,
# leading to an unpredictable order relative to the insertion sequence.

# heapsort is NOT a stable sorting algorithm. Items with equal keys
# will not necessarily have the same order as in the input sequence

#if we are doing arbitrary priority key updates or item add/removals,
#the ordering of items with equal keys will depend on the history

#if we want a strict ordering of items with equal keys, we need to
#overload __lt__ to handle tie-breaking (resolve into a strict ordering of the entries)



if __name__ == '__main__':
    unittest.main()

