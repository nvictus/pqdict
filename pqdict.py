"""Copyright (c) 2012 Nezar Abdennur

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

"""Priority Queue Dictionary -- An indexed priority queue data structure.

Inspired by the Python implementation of the heapq module, which was written by 
Kevin O'Connor and augmented by Tim Peters and Raymond Hettinger.

A dict-like heap queue to prioritize hashable objects while providing random 
access and updatable priorities.

The priority queue is implemented as a binary heap, which supports:         
    - O(1) access to the top priority element        
    - O(log n) removal of the top priority element     
    - O(log n) insertion of a new element

In addition, an internal dictionary or "index" maps elements to their position
in the heap array. This index is kept up-to-date when the heap is manipulated.
As a result, PQD also supports:          
    - O(1) lookup of an arbitrary element's priority key     
    - O(log n) removal of an arbitrary element          
    - O(log n) updating of an arbitrary element's priority key

The standard heap operations used internally are based on those in the python
heapq module (here, called "sink" and "swim").* These operations are extended to
maintain the internal dictionary.

* The names of the methods in heapq (sift up/down) refer to the motion of the
items being compared to, rather than the item being operated on as is usually
done in textbooks (i.e. bubble down/up, instead). I stuck to the textbook
convention, but using the sink/swim nomenclature from Sedgewick et al: the way
I like to think of it, an item that is too "heavy" (low-priority) should sink
down the tree, while one that is too "light" should float or swim up.

Implementation details:
    _heap (list): stores (dkey, pkey) pairs as "entry" objects that implement
                  __lt__ which defines how their priority keys are compared
    _position (dict): maps each dkey to the index of its entry in the heap

""" 
__version__ = (0, 5, 0)
__all__ = ['PQDict', 'sort_by_value', 'nlargest', 'nsmallest', 'consume']

import sys
from collections import Mapping, MutableMapping
if sys.version_info[0] < 3:
    range = xrange

class _AbstractEntry(object):
    """
    The internal heap items of a PQDict.

    The heap algorithms use the "<" comparator to compare entries, so
    subclasses must implement __lt__.

    """
    __slots__ = ('dkey', 'pkey')
    def __init__(self, dkey, pkey):
        self.dkey = dkey
        self.pkey = pkey

    def __lt__(self, other):
        raise NotImplementedError

    def __repr__(self):
        return self.__class__.__name__ + \
            "(%s: %s)" % (repr(self.dkey), self.pkey)

class _MinEntry(_AbstractEntry):
    """
    Entries for a PQDict backed by a min-heap.

    """
    __slots__ = ()
    __init__ = _AbstractEntry.__init__
    def __eq__(self, other):
        return self.pkey == other.pkey
    def __lt__(self, other):
        return self.pkey < other.pkey

class _MaxEntry(_AbstractEntry):
    """
    Entries for a PQDict backed by a max-heap.

    """
    __slots__ = ()
    __init__ = _AbstractEntry.__init__
    def __eq__(self, other):
        return self.pkey == other.pkey
    def __lt__(self, other):
        return self.pkey > other.pkey

def new_entry_class(comparator):
    """
    Define entries for a PQDict that uses a custom comparator to sort entries.
    The comparator should have the form:

        cmp( self, other ) --> bool

    where self and other are entry instances (have dkey and pkey attributes).
    The function should return True if self has higher priority than other and 
    False otherwise.
    
    """
    class _CustomEntry(_AbstractEntry):
        __lt__ = comparator
    return _CustomEntry


class PQDict(MutableMapping):
    """
    A mapping object that maps dictionary keys (dkeys) to priority keys (pkeys). 
    PQDicts maintain an internal heap so that the highest priority item can 
    always be obtained in constant time. The mapping is mutable so items may be 
    added, removed and have their priorities updated without breaking the heap.

    """
    _entry_class = _MinEntry

    __eq__ = MutableMapping.__eq__
    __ne__ = MutableMapping.__ne__
    keys = MutableMapping.keys
    values = prioritykeys = MutableMapping.values
    items = MutableMapping.items
    get = MutableMapping.get
    clear = MutableMapping.clear
    update = MutableMapping.update
    setdefault = MutableMapping.setdefault

    def __init__(self, *args, **kwargs):
        """
        Same input signature as dict:
        Accepts at most one positional argument:
            - a sequence/iterator of (dkey, pkey) pairs
            - a mapping object
        Accepts keyword arguments

        The default priority ordering for entries is in decreasing pkey value
        (i.e., a min-pq: SMALLER pkey values have a HIGHER rank).

        """
        if len(args) > 1:
            raise TypeError('Too many arguments')

        self._heap = []
        self._position = {}

        pos = 0
        if args:
            if isinstance(args[0], Mapping) or hasattr(args[0], 'items'):
                seq = args[0].items()
            else:
                seq = args[0]
            for dkey, pkey in seq:
                entry = self._entry_class(dkey, pkey)
                self._heap.append(entry)
                self._position[dkey] = pos
                pos += 1
        if kwargs:
            for dkey, pkey in kwargs.items():
                entry = self._entry_class(dkey, pkey)
                self._heap.append(entry)
                self._position[dkey] = pos
                pos += 1
        self._heapify()

    @classmethod
    def minpq(cls, *args, **kwargs):
        """
        Create a new Min-PQDict. Smaller priority keys confer higher rank.

        """
        pq = cls()
        pq._entry_class = _MinEntry
        pq.__init__(*args, **kwargs)
        return pq

    @classmethod
    def maxpq(cls, *args, **kwargs):
        """
        Create a new Max-PQDict. Larger priority keys confer higher rank.

        """
        pq = cls()
        pq._entry_class = _MaxEntry
        pq.__init__(*args, **kwargs)
        return pq

    @classmethod
    def fromkeys(cls, iterable, value=None, rank_by=None, maxpq=False):
        """
        Create a new PQDict with dictionary keys from an iterable and priority 
        keys set to value (default value is +inf or -inf to start items off at
        the bottom of the queue). If a function rank_by is provided instead, 
        that function is used to compute a priority key for each object in the 
        iterable.

        """
        if value and rank_by:
            raise TypeError("Received both 'value' and 'rank_by' argument.")

        if value is None:
            value = float('-inf') if maxpq else float('inf')

        if maxpq:
            cls = cls.maxpq

        if rank_by is None:
            return cls( (dkey, value) for dkey in iterable )
        else:
            return cls( (dkey, rank_by(dkey)) for dkey in iterable )

    @classmethod
    def create(cls, prio):
        """
        Create an empty PQDict that uses a custom comparator. The comparator 
        should have the form:

            prio( self, other ) --> bool

        where self and other are entry instances (have dkey and pkey members).
        The function should return True if self has higher priority than other 
        and False otherwise.

        If prio is a PQDict instance instead of a function, then an empty PQDict 
        using the same comparator is returned.

        """
        pq = cls()
        if isinstance(prio, PQDict):
            pq._entry_class = prio._entry_class
        else:
            pq._entry_class = new_entry_class(prio)
        return pq

    @property
    def pq_type(self):
        if self._entry_class == _MinEntry:
            return 'min'
        elif self._entry_class == _MaxEntry:
            return 'max'
        else:
            return 'custom'

    def __len__(self):
        """
        Return number of items in the PQD.

        """
        return len(self._heap)

    def __contains__(self, dkey):
        """
        Return True if dkey is in the PQD else return False.

        """
        return dkey in self._position

    def __iter__(self):
        """
        Return an iterator over the dictionary keys of the PQD. The order 
        of iteration is arbitrary! Use iterkeys() to iterate over dictionary 
        keys in order of priority.

        """
        for entry in self._heap:
            yield entry.dkey

    def __getitem__(self, dkey):
        """
        Return the priority key of dkey. Raises a KeyError if not in the PQD.

        """
        return self._heap[self._position[dkey]].pkey #raises KeyError

    def __setitem__(self, dkey, pkey):
        """
        Assign a priority key to a dictionary key.

        """
        heap = self._heap
        position = self._position
        try:
            pos = position[dkey]
        except KeyError:
            # add new entry:
            # put the new entry at the end and let it bubble up
            n = len(self._heap)
            self._heap.append(self._entry_class(dkey, pkey))
            self._position[dkey] = n
            self._swim(n)
        else:
            # update existing entry:
            # bubble up or down depending on pkeys of parent and children
            heap[pos].pkey = pkey
            parent_pos = (pos - 1) >> 1
            child_pos = 2*pos + 1
            if parent_pos > -1 and heap[pos] < heap[parent_pos]:
                self._swim(pos)
            elif child_pos < len(heap):
                other_pos = child_pos + 1
                if (other_pos < len(heap) 
                        and not heap[child_pos] < heap[other_pos]):
                    child_pos = other_pos
                if heap[child_pos] < heap[pos]:
                    self._sink(pos)

    def __delitem__(self, dkey):
        """
        Remove item. Raises a KeyError if dkey is not in the PQD.

        """
        heap = self._heap
        position = self._position
        pos = position.pop(dkey) #raises appropriate KeyError

        # Take the very last entry and place it in the vacated spot. Let it
        # sink or swim until it reaches its new resting place.
        entry_to_delete = heap[pos]
        end = heap.pop(-1)
        if end is not entry_to_delete:
            heap[pos] = end
            position[end.dkey] = pos

            parent_pos = (pos - 1) >> 1
            child_pos = 2*pos + 1
            if parent_pos > -1 and heap[pos] < heap[parent_pos]:
                self._swim(pos)
            elif child_pos < len(heap):
                other_pos = child_pos + 1
                if (other_pos < len(heap) and
                        not heap[child_pos] < heap[other_pos]):
                    child_pos = other_pos
                if heap[child_pos] < heap[pos]:
                    self._sink(pos)
        del entry_to_delete

    def __copy__(self):
        """
        Return a new PQD containing the same dkeys associated with the same 
        priority key values.

        """
        from copy import copy
        other = self.__class__()
        # Entry objects are mutable and should not be shared by different PQDs.
        other._heap = [copy(entry) for entry in self._heap]
        # It's safe to just copy the _position dict (dkeys->int)
        other._position = copy(self._position)
        return other
    copy = __copy__

    def __repr__(self):
        things = ', '.join(['%s: %s' % (repr(entry.dkey), entry.pkey) 
                                for entry in self._heap])
        return self.__class__.__name__ + '({' + things  + '})'

    __marker = object()
    def pop(self, dkey=__marker, default=__marker):
        """
        If dkey is in the PQD, remove it and return its priority key, else 
        return default. If default is not provided and dkey is not in the PQD, 
        raise a KeyError.

        If dkey is not provided, remove and return the top-priority dictionary
        key or raise KeyError if the PQD is empty.

        """
        heap = self._heap
        position = self._position

        if dkey is self.__marker:
            if not heap:
                raise KeyError('PQDict is empty')
            dkey = heap[0].dkey
            del self[dkey]
            return dkey

        try:
            pos = position.pop(dkey) #raises appropriate KeyError
        except KeyError:
            if default is self.__marker:
                raise
            return default
        else:
            entry_to_delete = heap[pos]
            pkey = entry_to_delete.pkey
            end = heap.pop(-1)
            if end is not entry_to_delete:
                heap[pos] = end
                position[end.dkey] = pos

                parent_pos = (pos - 1) >> 1
                child_pos = 2*pos + 1
                if parent_pos > -1 and heap[pos] < heap[parent_pos]:
                    self._swim(pos)
                elif child_pos < len(heap):
                    other_pos = child_pos + 1
                    if (other_pos < len(heap) 
                            and not heap[child_pos] < heap[other_pos]):
                        child_pos = other_pos
                    if heap[child_pos] < heap[pos]:
                        self._sink(pos)
            del entry_to_delete
            return pkey

    def top(self):
        """
        Get the top priority dictionary key. Raises KeyError if PQD is empty.

        """
        try:
            entry = self._heap[0]
        except IndexError:
            raise KeyError('PQDict is empty')
        return entry.dkey

    def popitem(self):
        """
        Extract top priority dictionary key and priority key. Raises KeyError if 
        PQD is empty.

        """
        heap = self._heap
        position = self._position

        try:
            end = heap.pop(-1)
        except IndexError:
            raise KeyError('PQDict is empty')

        if heap:
            entry = heap[0]
            heap[0] = end
            position[end.dkey] = 0
            self._sink(0)
        else:
            entry = end
        del position[entry.dkey]
        return entry.dkey, entry.pkey

    def topitem(self):
        """
        Get top priority dictionary key and priority key. Raises KeyError if PQD 
        is empty.

        """
        try:
            entry = self._heap[0]
        except IndexError:
            raise KeyError('PQDict is empty')
        return entry.dkey, entry.pkey

    def additem(self, dkey, pkey):
        """
        Add a new item. Raises KeyError if dkey is already in the PQD.

        """
        if dkey in self._position:
            raise KeyError('%s is already in the queue' % repr(dkey))
        self[dkey] = pkey

    def pushpopitem(self, dkey, pkey):
        """
        Equivalent to inserting a new item followed by removing the top priority 
        item, but faster. Raises KeyError if the new dkey is already in the PQD.

        """
        heap = self._heap
        position = self._position
        entry = self._entry_class(dkey, pkey)

        if dkey in self:
            raise KeyError('%s is already in the queue' % repr(dkey))

        if heap and heap[0] < entry:
            entry, heap[0] = heap[0], entry
            position[dkey] = 0
            del position[entry.dkey]
            self._sink(0)

        return entry.dkey, entry.pkey

    def updateitem(self, dkey, new_pkey):
        """
        Update the priority key of an existing item. Raises KeyError if dkey is
        not in the PQD.

        """
        if dkey not in self._position:
            raise KeyError(dkey)
        self[dkey] = new_pkey

    def replace_key(self, dkey, new_dkey):
        """
        Replace the dictionary key of an existing heap entry in place. Raises 
        KeyError if the dkey to replace does not exist or if the new dkey is 
        already in the PQD.

        """
        heap = self._heap
        position = self._position

        if new_dkey in self:
            raise KeyError('%s is already in the queue' % repr(new_dkey))

        pos = position.pop(dkey) #raises appropriate KeyError
        position[new_dkey] = pos
        heap[pos].dkey = new_dkey

    def swap_priority(self, dkey1, dkey2):
        """
        Fast way to swap the priorities of two items in the PQD. Raises KeyError
        if either dictionary key does not exist.

        """
        heap = self._heap
        position = self._position

        if dkey1 not in self or dkey2 not in self:
            raise KeyError

        pos1, pos2 = position[dkey1], position[dkey2]
        heap[pos1].dkey, heap[pos2].dkey = dkey2, dkey1
        position[dkey1], position[dkey2] = pos2, pos1

    def iterkeys(self):
        """
        Destructive heapsort iterator over dictionary keys, ordered by priority
        key.

        """
        try:
            while True:
                yield self.popitem()[0]
        except KeyError:
            return

    def itervalues(self):
        """
        Destructive heapsort iterator over priority keys.

        """
        try:
            while True:
                yield self.popitem()[1]
        except KeyError:
            return
    iterprioritykeys = itervalues

    def iteritems(self):
        """
        Destructive heapsort iterator over items, ordered by priority key.

        """
        try:
            while True:
                yield self.popitem()
        except KeyError:
            return

    def _heapify(self):
        n = len(self._heap)
        for pos in reversed(range(n//2)):
            self._sink(pos)

    def _sink(self, top=0):
        # "Sink-to-the-bottom-then-swim" algorithm (Floyd, 1964)
        # Tends to reduce the number of comparisons when inserting "heavy" items
        # at the top, e.g. during a heap pop. See heapq for more details.
        heap = self._heap
        position = self._position
        endpos = len(heap)

        # Grab the top entry
        pos = top
        entry = heap[pos]

        # Sift up a chain of child nodes
        child_pos = 2*pos + 1
        while child_pos < endpos:
            # Choose the smaller child.
            other_pos = child_pos + 1
            if other_pos < endpos and not heap[child_pos] < heap[other_pos]:
                child_pos = other_pos
            child_entry = heap[child_pos]

            # Move it up one level.
            heap[pos] = child_entry
            position[child_entry.dkey] = pos

            # Next level
            pos = child_pos
            child_pos = 2*pos + 1

        # We are left with a "vacant" leaf. Put our entry there and let it swim 
        # until it reaches its new resting place.
        heap[pos] = entry
        position[entry.dkey] = pos
        self._swim(pos, top)

    def _swim(self, pos, top=0):
        heap = self._heap
        position = self._position

        # Grab the entry from its place
        entry = heap[pos]

        # Sift parents down until we find a place where the entry fits.
        while pos > top:
            parent_pos = (pos - 1) >> 1
            parent_entry = heap[parent_pos]
            if entry < parent_entry:
                heap[pos] = parent_entry
                position[parent_entry.dkey] = pos
                pos = parent_pos
                continue
            break

        # Put entry in its new place
        heap[pos] = entry
        position[entry.dkey] = pos

def sort_by_value(mapping, reverse=False):
    """
    Takes a mapping and, treating the values as priority keys, sorts its items 
    by value via heapsort using a PQDict.

    Equivalent to: sorted(mapping.items(), key=itemgetter(1), reverse=reverse),
    except it returns a generator.

    Returns:
        an iterator over the dictionary items sorted by value

    """
    if reverse:
        pq = PQDict.maxpq(mapping)
    else:
        pq = PQDict(mapping)
    return pq.iteritems()

def nlargest(n, mapping):
    """
    Takes a mapping and returns the n keys associated with the largest values 
    in descending order. If the mapping has fewer than n items, all its keys are
    returned.

    Returns:
        a list of up to n dictionary keys

    """
    try:
        it = mapping.iteritems()
    except AttributeError:
        it = iter(mapping.items())

    pq = PQDict.minpq()
    try:
        for i in range(n):
            pq.additem(*next(it))
    except StopIteration:
        pass

    try:
        while it:
            pq.pushpopitem(*next(it))
    except StopIteration:
        pass

    out = list(pq.iterkeys())
    out.reverse()
    return out

def nsmallest(n, mapping):
    """
    Takes a mapping and returns the n keys associated with the smallest values 
    in ascending order. If the mapping has fewer than n items, all its keys are
    returned.

    Returns:
        a list of up to n dictionary keys

    """
    try:
        it = mapping.iteritems()
    except AttributeError:
        it = iter(mapping.items())

    pq = PQDict.maxpq()
    try:
        for i in range(n):
            pq.additem(*next(it))
    except StopIteration:
        pass

    try:
        while it:
            pq.pushpopitem(*next(it))
    except StopIteration:
        pass

    out = list(pq.iterkeys())
    out.reverse()
    return out

def consume(*pq_dicts):
    """
    Combine multiple priority queue dictionaries into a single prioritized 
    output stream. Assumes all the priority queues use the same comparator and 
    all priority keys are comparable.

    Returns: 
        a generator that yields (dkey, pkey) pairs from all the PQDs

    """
    iterators = []
    for pq in pq_dicts:
        iterators.append(pq.iteritems())

    collector = PQDict.create(pq)
    for i, it in enumerate(iterators): 
        try:
            collector[i] = next(it)[::-1]
        except StopIteration:
            pass

    while collector:
        i, item = collector.popitem()
        yield item[::-1]

        try:
            collector[i] = next(iterators[i])[::-1]
        except StopIteration:
            pass
    return

