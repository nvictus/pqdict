"""
Priority Queue Dictionary -- An indexed priority queue data structure.

Stores a set of prioritized hashable items. Useful as an updatable schedule.

The priority queue is implemented as a binary min heap, which supports:
    - O(1) access to the minimum item
    - O(log n) insertion of a new item
    - O(log n) deletion of the minimum item

In addition, an internal dictionary or "index" maps items to their position in
the heap array. This index is kept up-to-date when the heap is manipulated. As a
result, PQD also supports:
    - O(1) lookup of an arbitrary item's priority key
    - O(log n) deletion of an arbitrary item
    - O(log n) updating of an arbitrary item's priority key

The standard heap operations used internally (here, called "sink" and "swim")
are based on the code in the python heapq module*. These operations are
augmented to maintain the internal index dictionary.

* The names of the methods in heapq (sift up/down) seem to refer to the motion
of the items being compared to, rather than the item being operated on as is
normally done in textbooks (i.e. sift down/up, instead). I stuck to the textbook
convention, but using the sink/swim nomenclature from Sedgewick et al: the way
I see it, an item that is too "heavy" (low-priority) should sink down the tree,
while one that is too "light" should float or swim up. Note, however, that the
sink implementation is non-conventional. See heapq for details about why.

"""
#!/usr/bin/env python
__author__ = ('Nezar Abdennur', 'nabdennur@gmail.com')

import collections

class PQEntry(object):
    def __init__(self, priority, key):
        self.priority = priority
        self.key = key

    def __lt__(self, other):
        return self.priority < other.priority

    def __eq__(self, other):
        return self.priority == other.priority

    def __le__(self, other):
        return self.priority < other.priority or self.priority == other.priority

    def __repr__(self):
        return "PQEntry(" + str(self.key) + ": " + str(self.priority) + ")"


# Sized: __len__
# Container: __contains__
# Iterable: __iter__
# Mapping: __getitem__, __contains__, __eq__*, __ne__*, get*, keys*, values*, items*
# MutableMapping: __setitem__, __delitem__, pop, popitem, clear*, update*, setdefault*
# This class: add, peek, updateitem
#
# *inherited methods

class PriorityQueueDict(collections.MutableMapping):
    __slots__ = ('heap', 'nodefinder')

    def __init__(self, *args, **kwargs):
        self.heap = []
        self.nodefinder = {}
        if args or kwargs:
            d = dict(*args, **kwargs)
            for dkey, pkey in d.items():
                self[dkey] = pkey
            self._heapify()
        #TODO: improve constructor?
        # use cmp function to set custom comparator function for PQEntry?
        # or find some other way to override __lt__, e.g. for a MaxPQ or for tie-breaking

    def __len__(self):
        """
        Return number of items in the PQD.

        """
        return len(self.nodefinder)

    def __contains__(self, dict_key):
        """
        Return True if dict_key is in the PQD else return False.

        """
        return dict_key in self.nodefinder

    def __iter__(self):
        """
        Return an iterator over the keys of the PQD.

        """
        return self.nodefinder.__iter__()

    def __getitem__(self, dict_key):
        """
        Return the priority of dict_key. Raises a KeyError if not in the PQD.

        """
        return self.heap[self.nodefinder[dict_key]].priority #raises KeyError

    def __setitem__(self, dict_key, priority_key):
        """
        Set priority key of dict_key item.

        """
        heap = self.heap
        finder = self.nodefinder
        try:
            pos = finder[dict_key]
        except KeyError:
            # add new entry
            n = len(self.heap)
            self.heap.append(PQEntry(priority_key, dict_key))
            self.nodefinder[dict_key] = n
            self._swim(n)
        else:
            # update existing entry
            heap[pos].priority = priority_key
            parent_pos = (pos - 1) >> 1
            child_pos = 2*pos + 1
            if parent_pos > 0 and heap[pos] < heap[parent_pos]:
                self._swim(pos)
            elif child_pos < len(heap):
                right_pos = child_pos + 1
                if right_pos < len(heap) and not heap[child_pos] < heap[right_pos]:
                    child_pos = right_pos
                if heap[child_pos] < heap[pos]:
                    self._sink(pos)

    def __delitem__(self, dict_key):
        """
        Remove dict_key item. Raises a KeyError if key is not in the PQD.

        """
        heap = self.heap
        finder = self.nodefinder

        # Remove very last item and place in vacant spot. Let the new item
        # sink until it reaches its new resting place.
        try:
            pos = finder.pop(dict_key)
        except KeyError:
            raise
        else:
            entry = heap[pos]
            last = heap.pop(-1)
            if entry is not last:
                heap[pos] = last
                finder[last.key] = pos
                self._sink(pos)
                self._swim(pos)
            del entry

    def __copy__(self):
        """
        Return a new PQD with the same dict_keys (shallow copied) and priorities.

        """
        #TODO: deep copy priority keys? shouldn't these always be int/float anyway?
        from copy import copy
        other = PriorityQueueDict()
        other.heap = [copy(entry) for entry in self.heap]
        other.nodefinder = copy(self.nodefinder)
        return other

    copy = __copy__
    __eq__ = collections.MutableMapping.__eq__
    __ne__ = collections.MutableMapping.__ne__
    get = collections.MutableMapping.get
    keys = collections.MutableMapping.keys
    values = collections.MutableMapping.values
    items = collections.MutableMapping.items
    clear = collections.MutableMapping.clear
    update = collections.MutableMapping.update
    setdefault = collections.MutableMapping.setdefault
    __marker = object()

    def pop(self, dict_key, default=__marker):
        """
        If key is in the PQD, remove it and return its priority key, else return
        default. If default is not given and dict_key is not in the PQD, a
        KeyError is raised.

        """
        heap = self.heap
        finder = self.nodefinder

        try:
            pos = finder.pop(dict_key)
        except KeyError:
            if default is self.__marker:
                raise
            return default
        else:
            delentry = heap[pos]
            last = heap.pop(-1)
            if delentry is not last:
                heap[pos] = last
                finder[last.key] = pos
                self._sink(pos)
                self._swim(pos)
            pkey = delentry.priority
            del delentry
            return pkey

    def popitem(self):
        """
        Extract priority item. Raises KeyError if PQD is empty.

        """
        try:
            last = self.heap.pop(-1)
        except IndexError:
            raise KeyError
        else:
            if self.heap:
                entry = self.heap[0]
                self.heap[0] = last
                self.nodefinder[last.key] = 0
                self._sink(0)
            else:
                entry = last
            self.nodefinder.pop(entry.key)
            return entry.key, entry.priority

    def add(self, dict_key, priority_key):
        """
        Add a new item. Raises KeyError if item is already in the map.

        """
        if dict_key in self.nodefinder:
            raise KeyError
        self[dict_key] = priority_key

    def updateitem(self, dict_key, new_priority):
        """
        Update the priority key of an existing item. Raises KeyError if item is
        not in the PQD.

        """
        if dict_key not in self.nodefinder:
            raise KeyError
        self[dict_key] = new_priority

    def peek(self):
        """
        Get priority item.

        """
        try:
            entry = self.heap[0]
        except IndexError:
            raise KeyError
        return entry.key, entry.priority

    @staticmethod
    def fromkeyfunction(iterable, key):
        """
        Provide a key function that determines priorities by which to heapify
        the elements of an iterable into a PQD.

        """
        pq = PriorityQueueDict()
        i = 0
        for item in iterable:
            entry = PQEntry(key(item), item)
            pq.heap.append(entry)
            pq.nodefinder[entry.key] = i
            i += 1
        pq._heapify()
        return pq

    def _sink(self, top=0):
        heap = self.heap
        finder = self.nodefinder

        # Peel off top item
        pos = top
        item = heap[pos]

        # Sift up a trail of child nodes
        child_pos = 2*pos + 1
        while child_pos < len(heap):
            # Choose the index of smaller child.
            right_pos = child_pos + 1
            if right_pos < len(heap) and not heap[child_pos] < heap[right_pos]:
                child_pos = right_pos

            # Move the smaller child up.
            child_item = heap[child_pos]
            heap[pos] = child_item
            finder[child_item.key] = pos

            pos = child_pos
            child_pos = 2*pos + 1

        # We are now at a leaf. Put item there and let it swim until it reaches
        # its new resting place.
        heap[pos] = item
        finder[item.key] = pos
        self._swim(pos, top)

    def _swim(self, pos, top=0):
        heap = self.heap
        finder = self.nodefinder

        # Remove item from its place
        item = heap[pos]

        # Bubble item up by sifting parents down until finding a place it fits.
        while pos > top:
            parent_pos = (pos - 1) >> 1
            parent_item = heap[parent_pos]
            if item < parent_item:
                heap[pos] = parent_item
                finder[parent_item.key] = pos
                pos = parent_pos
                continue
            break

        # Put item in its new place
        heap[pos] = item
        finder[item.key] = pos

    def _heapify(self):
        n = len(self.heap)
        for pos in reversed(range(n//2)):
            self._sink(pos)



if __name__ == '__main__':
    pq = PriorityQueueDict()
    pq.add('A', 5.69)
    pq.add('B', 3.22)
    pq.add('C', 9.85)
    pq.add('D', 4.92)
    pq.add('E', 1.99)
    pq.add('F', 0.24)
    pq.add('G',14.01)

    print()




##def heapify(x):
##    n = len(x)
##    for i in reversed(range(n//2)):
##        _sink(x, i)
##
##def heappush(heap, item):
##    heap.append(item)
##    _swim(heap, len(heap)-1)
##
##def heappop(heap):
##    last = heap.pop(-1)
##    if heap:
##        item = heap[0]
##        heap[0] = last
##        _sink(heap, 0)
##    else:
##        item = last
##    return item
##
##def heapupdate(heap, pos, new_item):
##    heap[pos] = new_item
##    _update_reheapify(heap, pos)










