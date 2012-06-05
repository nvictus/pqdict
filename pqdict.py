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

class PQDEntry(object):
    def __init__(self, item, pkey):
        self.item = item
        self.pkey = pkey

    def __lt__(self, other):
        # override __lt__, e.g. for a MaxPQ or for tie-breaking rules
        raise NotImplementedError

    def __eq__(self, other):
        return self.pkey == other.pkey

    def __repr__(self):
        return "PQDEntry(%s: %s)"%(repr(self.item),self.pkey)

class MinPQDEntry(PQDEntry):
    def __lt__(self, other):
        return self.pkey < other.pkey

class MaxPQDEntry(PQDEntry):
    def __lt__(self, other):
        return self.pkey > other.pkey

class PriorityQueueDictionary(collections.MutableMapping):
    """
    Maps dictionary keys (keys) to priority keys (values). Maintains an
    internal heap so that the highest priority item can always be obtained in
    constant time. The mapping is fully mutable so items may be added, removed
    and have their priorities updated.

    """
    __slots__ = ('heap', 'nodefinder','create_entry')

    def __init__(self, *args, maxheap=False, **kwargs):
        """
        Mimics the standard dict constructor:
            Accepts a sequence/iterator of (dkey, pkey) tuples.
            Accepts named arguments as dkey=pkey or an unpacked dictionary.
            Also accepts a single mapping object to convert it to a pqdict.

        The default priority ranking for entries is in decreasing pkey value
        (i.e., a min-pq: LOWER pkey values have a HIGHER rank). This is typical
        for a scheduler, where the higher priority tasks have earlier times.
        Setting the maxheap parameter to True creates a max-pq where higher pkey
        values have a higher rank.

        heap (list): stores dkey,pkey-pairs as "entries" (PQDEntry objects).
        nodefinder (dict): maps each dkey to the index of its entry in the heap
        create_entry (class): entry type (< comparator is used to rank entries)

        """
        self.heap = []
        self.nodefinder = {}
        pos = 0
        if len(args) > 1:
            raise TypeError
        if maxheap:
            self.create_entry = MaxPQDEntry
        else:
            self.create_entry = MinPQDEntry
        if args:
            if isinstance(args[0], collections.Mapping):
                seq = args[0].items()
            else:
                seq = args[0]
            try:
                for dkey, pkey in seq:
                    entry = self.create_entry(dkey, pkey)
                    self.heap.append(entry)
                    self.nodefinder[dkey] = pos
                    pos += 1
            except TypeError:
                raise ValueError
        if kwargs:
            for dkey, pkey in kwargs.items():
                entry = self.create_entry(dkey, pkey)
                self.heap.append(entry)
                self.nodefinder[dkey] = pos
                pos += 1
        self._heapify()

    def __len__(self):
        """
        Return number of items in the PQD.

        """
        return len(self.nodefinder)

    def __contains__(self, dkey):
        """
        Return True if dkey is in the PQD else return False.

        """
        return dkey in self.nodefinder

    def __iter__(self):
        """
        Return an iterator over the keys of the PQD.

        """
        for entry in self.heap:
            yield entry.item

    def __getitem__(self, dkey):
        """
        Return the priority of dkey. Raises a KeyError if not in the PQD.

        """
        return self.heap[self.nodefinder[dkey]].pkey #raises KeyError

    def __setitem__(self, dkey, pkey):
        """
        Set priority key of item dkey.

        """
        heap = self.heap
        finder = self.nodefinder
        try:
            pos = finder[dkey]
        except KeyError:
            # add new entry
            n = len(self.heap)
            self.heap.append(self.create_entry(dkey, pkey))
            self.nodefinder[dkey] = n
            self._swim(n)
        else:
            # update existing entry
            heap[pos].pkey = pkey
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

    def __delitem__(self, dkey):
        """
        Remove item dkey. Raises a KeyError if dkey is not in the PQD.

        """
        heap = self.heap
        finder = self.nodefinder

        # Remove very last item and place in vacant spot. Let the new item
        # sink until it reaches its new resting place.
        try:
            pos = finder.pop(dkey)
        except KeyError:
            raise
        else:
            entry = heap[pos]
            last = heap.pop(-1)
            if entry is not last:
                heap[pos] = last
                finder[last.item] = pos
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
            del entry

    def __copy__(self):
        """
        Return a new PQD with the same dkeys (shallow copied) and priority keys.

        """
        #TODO: deep copy priority keys? shouldn't these always be int/float anyway?
        from copy import copy
        other = PriorityQueueDictionary()
        other.heap = [copy(entry) for entry in self.heap]
        other.nodefinder = copy(self.nodefinder)
        return other
    copy = __copy__

    def __repr__(self):
        things = ',\n '.join(['%s: %s'%(repr(entry.item), entry.pkey) for entry in self.heap])
        return 'pqdict(\n{' + things  + '}\n)'

    __marker = object()

    def pop(self, dkey, default=__marker):
        """
        If key is in the PQD, remove it and return its priority key, else return
        default. If default is not given and dkey is not in the PQD, a KeyError
        is raised.

        """
        heap = self.heap
        finder = self.nodefinder

        try:
            pos = finder.pop(dkey)
        except KeyError:
            if default is self.__marker:
                raise
            return default
        else:
            delentry = heap[pos]
            last = heap.pop(-1)
            if delentry is not last:
                heap[pos] = last
                finder[last.item] = pos
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
            pkey = delentry.pkey
            del delentry
            return pkey

    def popitem(self):
        """
        Extract top priority item. Raises KeyError if PQD is empty.

        """
        try:
            last = self.heap.pop(-1)
        except IndexError:
            raise KeyError
        else:
            if self.heap:
                entry = self.heap[0]
                self.heap[0] = last
                self.nodefinder[last.item] = 0
                self._sink(0)
            else:
                entry = last
            self.nodefinder.pop(entry.item)
            return entry.item, entry.pkey

    def add(self, dkey, pkey):
        """
        Add a new item. Raises KeyError if item is already in the PQD.

        """
        if dkey in self.nodefinder:
            raise KeyError
        self[dkey] = pkey

    def updateitem(self, dkey, new_pkey):
        """
        Update the priority key of an existing item. Raises KeyError if item is
        not in the PQD.

        """
        if dkey not in self.nodefinder:
            raise KeyError
        self[dkey] = new_pkey

    def peek(self):
        """
        Get top priority item.

        """
        try:
            entry = self.heap[0]
        except IndexError:
            raise KeyError
        return entry.item, entry.pkey

    __eq__ = collections.MutableMapping.__eq__
    __ne__ = collections.MutableMapping.__ne__
    get = collections.MutableMapping.get
    keys = collections.MutableMapping.keys
    values = collections.MutableMapping.values
    items = collections.MutableMapping.items
    clear = collections.MutableMapping.clear
    update = collections.MutableMapping.update
    setdefault = collections.MutableMapping.setdefault

    @staticmethod
    def fromkeyfunction(iterable, keygen):
        """
        Provide a key function that determines priorities by which to heapify
        the elements of an iterable into a PQD.

        """
        return PriorityQueueDictionary((item, keygen(item)) for item in iterable)

    def _heapify(self):
        n = len(self.heap)
        for pos in reversed(range(n//2)):
            self._sink(pos)

    def _sink(self, top=0):
        heap = self.heap
        finder = self.nodefinder

        # Peel off top item
        pos = top
        entry = heap[pos]

        # Sift up a trail of child nodes
        child_pos = 2*pos + 1
        while child_pos < len(heap):
            # Choose the index of smaller child.
            right_pos = child_pos + 1
            if right_pos < len(heap) and not heap[child_pos] < heap[right_pos]:
                child_pos = right_pos

            # Move the smaller child up.
            child_entry = heap[child_pos]
            heap[pos] = child_entry
            finder[child_entry.item] = pos

            pos = child_pos
            child_pos = 2*pos + 1

        # We are now at a leaf. Put item there and let it swim until it reaches
        # its new resting place.
        heap[pos] = entry
        finder[entry.item] = pos
        self._swim(pos, top)

    def _swim(self, pos, top=0):
        heap = self.heap
        finder = self.nodefinder

        # Remove item from its place
        entry = heap[pos]

        # Bubble item up by sifting parents down until finding a place it fits.
        while pos > top:
            parent_pos = (pos - 1) >> 1
            parent_entry = heap[parent_pos]
            if entry < parent_entry:
                heap[pos] = parent_entry
                finder[parent_entry.item] = pos
                pos = parent_pos
                continue
            break

        # Put item in its new place
        heap[pos] = entry
        finder[entry.item] = pos


# Sized: __len__
# Container: __contains__
# Iterable: __iter__
# Mapping: __getitem__, __contains__, __eq__*, __ne__*, get*, keys*, values*, items*
# MutableMapping: __setitem__, __delitem__, pop, popitem, clear*, update*, setdefault*
# PriorityQueueDict: add, peek, updateitem
#
# *inherited methods


# NOTE: Items with equal keys will not necessarily have the same order as in
# the input sequence. If we are doing arbitrary priority key updates or item
# add/removals, the ordering of items with equal keys will depend on the history.

# We use a strict < comparison for bubbling the *entry* objects around. If we
# want a strict ordering of items with equal keys, we need to use an entry class
# with an overloaded __lt__  method to handle tie-breaking (resolve into a strict
# ordering of the items).

# e.g. use a named tuple to automatically get tie-breaking based on the natural
# ordering of the items, which must be unique since they are the dictionary keys.
# If the items in the PQD are not always comparable, then exploiting tuple
# comparison won't work.

# Also, to get max heap behavior, we overload __lt__ to return true when
# self.pkey > other.pkey

class RankedItemPQD(PriorityQueueDictionary):
    def __init__(self, *args, **kwargs):
        # change every pkey to [pkey, rank]
        pass

    def __setitem__(self, dkey, pkey):
        # change pkey to [pkey, len(self)+1]
        pass

    def __getitem__(self, dkey):
        # call super
        # return pkey[0]
        pass

    def peek(self):
        # call super
        # return dkey, pkey[0]
        pass

    def pop(self, dkey):
        # call super
        # return pkey[0]
        pass

    def popitem(self):
        # call super
        # return dkey, pkey[0]
        pass
