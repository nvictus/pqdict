# -*- coding: utf-8 -*-
"""
Priority Queue Dictionary (pqdict)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Pythonic indexed priority queue.

A dict-like heap queue to prioritize hashable objects while providing random
access and updatable priorities. Inspired by the ``heapq`` standard library
module, which was written by Kevin O'Connor and augmented by Tim Peters and
Raymond Hettinger.

The priority queue is implemented as a binary heap of (key, priority value)
pairs, which supports:

- O(1) search for the item with highest priority

- O(log n) removal of the item with highest priority

- O(log n) insertion of a new item

Additionally, an index maps elements to their location in the heap and is kept
up to date as the heap is manipulated. As a result, pqdict also supports:

- O(1) lookup of any item by key

- O(log n) removal of any item

- O(log n) updating of any item's priority level

Documentation at <http://pqdict.readthedocs.org/en/latest>.

:copyright: (c) 2012-2015 by Nezar Abdennur.
:license: MIT, see LICENSE for more details.

"""
try:
    from collections.abc import MutableMapping as _MutableMapping
except ImportError:
    # 2.7 compatability
    from collections import MutableMapping as _MutableMapping

from six.moves import range
from operator import lt, gt


__version__ = "1.1.1"
__all__ = ["pqdict", "PQDict", "minpq", "maxpq", "nlargest", "nsmallest"]


class _Node(object):
    __slots__ = ("key", "value", "prio")

    def __init__(self, key, value, prio):
        self.key = key
        self.value = value
        self.prio = prio

    def __repr__(self):
        return self.__class__.__name__ + "(%s, %s, %s)" % (
            repr(self.key),
            repr(self.value),
            repr(self.prio),
        )


class pqdict(_MutableMapping):
    """
    A collection that maps hashable objects (keys) to priority-determining
    values. The mapping is mutable so items may be added, removed and have
    their priority level updated.

    Parameters
    ----------
    data : mapping or iterable, optional
        Input data, e.g. a dictionary or a sequence of items.
    key : callable, optional
        Optional priority key function to transform values into priority keys
        for sorting. By default, the values are not transformed.
    reverse : bool, optional
        If ``True``, *larger* priority keys give items *higher* priority.
        Default is ``False``.
    precedes : callable, optional (overrides ``reverse``)
        Function that determines precedence of a pair of priority keys. The
        default comparator is ``operator.lt``, meaning *smaller* priority keys
        give items *higher* priority.

    """

    def __init__(self, data=None, key=None, reverse=False, precedes=lt):
        if reverse:
            if precedes == lt:
                precedes = gt
            else:
                raise ValueError("Got both `reverse=True` and a custom `precedes`.")

        if key is None or callable(key):
            self._keyfn = key
        else:
            raise ValueError(
                "`key` function must be a callable; got {}".format(type(key))
            )

        if callable(precedes):
            self._precedes = precedes
        else:
            raise ValueError(
                "`precedes` function must be a callable; got {}".format(type(precedes))
            )

        # The heap
        self._heap = []

        # The index
        self._position = {}

        if data is not None:
            self.update(data)

    @property
    def precedes(self):
        """Priority key precedence function"""
        return self._precedes

    @property
    def keyfn(self):
        """Priority key function"""
        return self._keyfn if self._keyfn is not None else lambda x: x

    def __repr__(self):
        things = ", ".join(
            ["%s: %s" % (repr(node.key), repr(node.value)) for node in self._heap]
        )
        return self.__class__.__name__ + "({" + things + "})"

    ############
    # dict API #
    ############
    __marker = object()
    __eq__ = _MutableMapping.__eq__
    __ne__ = _MutableMapping.__ne__
    keys = _MutableMapping.keys
    values = _MutableMapping.values
    items = _MutableMapping.items
    get = _MutableMapping.get
    clear = _MutableMapping.clear
    update = _MutableMapping.update
    setdefault = _MutableMapping.setdefault

    @classmethod
    def fromkeys(cls, iterable, value, **kwargs):
        """
        Return a new pqict mapping keys from an iterable to the same value.

        """
        return cls(((k, value) for k in iterable), **kwargs)

    def __len__(self):
        """
        Return number of items in the pqdict.

        """
        return len(self._heap)

    def __contains__(self, key):
        """
        Return ``True`` if key is in the pqdict.

        """
        return key in self._position

    def __iter__(self):
        """
        Return an iterator over the keys of the pqdict. The order of iteration
        is arbitrary! Use ``popkeys`` to iterate over keys in priority order.

        """
        for node in self._heap:
            yield node.key

    def __getitem__(self, key):
        """
        Return the priority value of ``key``. Raises a ``KeyError`` if not in
        the pqdict.

        """
        return self._heap[self._position[key]].value  # raises KeyError

    def __setitem__(self, key, value):
        """
        Assign a priority value to ``key``.

        """
        heap = self._heap
        position = self._position
        keygen = self._keyfn
        try:
            pos = position[key]
        except KeyError:
            # add
            n = len(heap)
            prio = keygen(value) if keygen is not None else value
            heap.append(_Node(key, value, prio))
            position[key] = n
            self._swim(n)
        else:
            # update
            prio = keygen(value) if keygen is not None else value
            heap[pos].value = value
            heap[pos].prio = prio
            self._reheapify(pos)

    def __delitem__(self, key):
        """
        Remove item. Raises a ``KeyError`` if key is not in the pqdict.

        """
        heap = self._heap
        position = self._position
        pos = position.pop(key)  # raises KeyError
        node_to_delete = heap[pos]
        # Take the very last node and place it in the vacated spot. Let it
        # sink or swim until it reaches its new resting place.
        end = heap.pop(-1)
        if end is not node_to_delete:
            heap[pos] = end
            position[end.key] = pos
            self._reheapify(pos)
        del node_to_delete

    def copy(self):
        """
        Return a shallow copy of a pqdict.

        """
        other = self.__class__(key=self._keyfn, precedes=self._precedes)
        other._position = self._position.copy()
        other._heap = [_Node(node.key, node.value, node.prio) for node in self._heap]
        return other

    def pop(self, key=__marker, default=__marker):
        """
        If ``key`` is in the pqdict, remove it and return its priority value,
        else return ``default``. If ``default`` is not provided and ``key`` is
        not in the pqdict, raise a ``KeyError``.

        If ``key`` is not provided, remove the top item and return its key, or
        raise ``KeyError`` if the pqdict is empty.

        """
        heap = self._heap
        position = self._position
        # pq semantics: remove and return top *key* (value is discarded)
        if key is self.__marker:
            if not heap:
                raise KeyError("pqdict is empty")
            key = heap[0].key
            del self[key]
            return key
        # dict semantics: remove and return *value* mapped from key
        try:
            pos = position.pop(key)  # raises KeyError
        except KeyError:
            if default is self.__marker:
                raise
            return default
        else:
            node_to_delete = heap[pos]
            end = heap.pop()
            if end is not node_to_delete:
                heap[pos] = end
                position[end.key] = pos
                self._reheapify(pos)
            value = node_to_delete.value
            del node_to_delete
            return value

    ######################
    # Priority Queue API #
    ######################
    def top(self):
        """
        Return the key of the item with highest priority. Raises ``KeyError``
        if pqdict is empty.

        """
        try:
            node = self._heap[0]
        except IndexError:
            raise KeyError("pqdict is empty")
        return node.key

    def popitem(self):
        """
        Remove and return the item with highest priority. Raises ``KeyError``
        if pqdict is empty.

        """
        heap = self._heap
        position = self._position

        try:
            end = heap.pop(-1)
        except IndexError:
            raise KeyError("pqdict is empty")

        if heap:
            node = heap[0]
            heap[0] = end
            position[end.key] = 0
            self._sink(0)
        else:
            node = end
        del position[node.key]
        return node.key, node.value

    def topitem(self):
        """
        Return the item with highest priority. Raises ``KeyError`` if pqdict is
        empty.

        """
        try:
            node = self._heap[0]
        except IndexError:
            raise KeyError("pqdict is empty")
        return node.key, node.value

    def additem(self, key, value):
        """
        Add a new item. Raises ``KeyError`` if key is already in the pqdict.

        """
        if key in self._position:
            raise KeyError("%s is already in the queue" % repr(key))
        self[key] = value

    def pushpopitem(self, key, value):
        """
        Equivalent to inserting a new item followed by removing the top
        priority item, but faster. Raises ``KeyError`` if the new key is
        already in the pqdict.

        """
        heap = self._heap
        position = self._position
        precedes = self._precedes
        prio = self._keyfn(value) if self._keyfn else value
        node = _Node(key, value, prio)
        if key in self:
            raise KeyError("%s is already in the queue" % repr(key))
        if heap and precedes(heap[0].prio, node.prio):
            node, heap[0] = heap[0], node
            position[key] = 0
            del position[node.key]
            self._sink(0)
        return node.key, node.value

    def updateitem(self, key, new_val):
        """
        Update the priority value of an existing item. Raises ``KeyError`` if
        key is not in the pqdict.

        """
        if key not in self._position:
            raise KeyError(key)
        self[key] = new_val

    def replace_key(self, key, new_key):
        """
        Replace the key of an existing heap node in place. Raises ``KeyError``
        if the key to replace does not exist or if the new key is already in
        the pqdict.

        """
        heap = self._heap
        position = self._position
        if new_key in self:
            raise KeyError("%s is already in the queue" % repr(new_key))
        pos = position.pop(key)  # raises appropriate KeyError
        position[new_key] = pos
        heap[pos].key = new_key

    def swap_priority(self, key1, key2):
        """
        Fast way to swap the priority level of two items in the pqdict. Raises
        ``KeyError`` if either key does not exist.

        """
        heap = self._heap
        position = self._position
        if key1 not in self or key2 not in self:
            raise KeyError
        pos1, pos2 = position[key1], position[key2]
        heap[pos1].key, heap[pos2].key = key2, key1
        position[key1], position[key2] = pos2, pos1

    def popkeys(self):
        """
        Heapsort iterator over keys in descending order of priority level.

        """
        try:
            while True:
                yield self.popitem()[0]
        except KeyError:
            return

    def popvalues(self):
        """
        Heapsort iterator over values in descending order of priority level.

        """
        try:
            while True:
                yield self.popitem()[1]
        except KeyError:
            return

    def popitems(self):
        """
        Heapsort iterator over items in descending order of priority level.

        """
        try:
            while True:
                yield self.popitem()
        except KeyError:
            return

    def heapify(self, key=__marker):
        """
        Repair a broken heap. If the state of an item's priority value changes
        you can re-sort the relevant item only by providing ``key``.

        """
        if key is self.__marker:
            n = len(self._heap)
            # No need to look at any node without a child.
            for pos in reversed(range(n // 2)):
                self._sink(pos)
        else:
            try:
                pos = self._position[key]
            except KeyError:
                raise KeyError(key)
            self._reheapify(pos)

    # Heap algorithms
    # The names of the heap operations in `heapq` (sift up/down) refer to the
    # motion of the nodes being compared to, rather than the node being
    # operated on as is usually done in textbooks (i.e. bubble down/up,
    # instead). Here I use the sink/swim nomenclature from
    # http://algs4.cs.princeton.edu/24pq/. The way I like to think of it, an
    # item that is too "heavy" (low-priority) should sink down the tree, while
    # one that is too "light" should float or swim up.
    def _reheapify(self, pos):
        # update existing node:
        # bubble up or down depending on values of parent and children
        heap = self._heap
        precedes = self._precedes
        parent_pos = (pos - 1) >> 1
        child_pos = 2 * pos + 1
        if parent_pos > -1 and precedes(heap[pos].prio, heap[parent_pos].prio):
            self._swim(pos)
        elif child_pos < len(heap):
            other_pos = child_pos + 1
            if other_pos < len(heap) and not precedes(
                heap[child_pos].prio, heap[other_pos].prio
            ):
                child_pos = other_pos
            if precedes(heap[child_pos].prio, heap[pos].prio):
                self._sink(pos)

    def _sink(self, top=0):
        # "Sink-to-the-bottom-then-swim" algorithm (Floyd, 1964)
        # Tends to reduce the number of comparisons when inserting "heavy"
        # items at the top, e.g. during a heap pop. See heapq for more details.
        heap = self._heap
        position = self._position
        precedes = self._precedes
        endpos = len(heap)
        # Grab the top node
        pos = top
        node = heap[pos]
        # Sift up a chain of child nodes
        child_pos = 2 * pos + 1
        while child_pos < endpos:
            # Choose the smaller child.
            other_pos = child_pos + 1
            if other_pos < endpos and not precedes(
                heap[child_pos].prio, heap[other_pos].prio
            ):
                child_pos = other_pos
            child_node = heap[child_pos]
            # Move it up one level.
            heap[pos] = child_node
            position[child_node.key] = pos
            # Next level
            pos = child_pos
            child_pos = 2 * pos + 1
        # We are left with a "vacant" leaf. Put our node there and let it swim
        # until it reaches its new resting place.
        heap[pos] = node
        position[node.key] = pos
        self._swim(pos, top)

    def _swim(self, pos, top=0):
        heap = self._heap
        position = self._position
        precedes = self._precedes
        # Grab the node from its place
        node = heap[pos]
        # Sift parents down until we find a place where the node fits.
        while pos > top:
            parent_pos = (pos - 1) >> 1
            parent_node = heap[parent_pos]
            if precedes(node.prio, parent_node.prio):
                heap[pos] = parent_node
                position[parent_node.key] = pos
                pos = parent_pos
                continue
            break
        # Put node in its new place
        heap[pos] = node
        position[node.key] = pos


###########
# Aliases #
###########

PQDict = pqdict  # deprecated


def minpq(*args, **kwargs):
    return pqdict(dict(*args, **kwargs), precedes=lt)


def maxpq(*args, **kwargs):
    return pqdict(dict(*args, **kwargs), precedes=gt)


#############
# Functions #
#############


def nlargest(n, mapping, key=None):
    """
    Takes a mapping and returns the n keys associated with the largest values
    in descending order. If the mapping has fewer than n items, all its keys
    are returned.

    Equivalent to:
        ``next(zip(*heapq.nlargest(mapping.items(), key=lambda x: x[1])))``

    Parameters
    ----------
    n : int
        The number of keys associated with the largest values
        in descending order
    mapping : Mapping
        A mapping object
    key : callable, optional
        Optional priority key function to transform values into priority keys
        for sorting. By default, the values are not transformed.

    Returns
    -------
    list of up to n keys from the mapping

    """
    try:
        it = mapping.iteritems()
    except AttributeError:
        it = iter(mapping.items())
    pq = pqdict(key=key, precedes=lt)
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
    out = list(pq.popkeys())
    out.reverse()
    return out


def nsmallest(n, mapping, key=None):
    """
    Takes a mapping and returns the n keys associated with the smallest values
    in ascending order. If the mapping has fewer than n items, all its keys are
    returned.

    Equivalent to:
        ``next(zip(*heapq.nsmallest(mapping.items(), key=lambda x: x[1])))``

    Parameters
    ----------
    n : int
        The number of keys associated with the smallest values
        in ascending order
    mapping : Mapping
        A mapping object
    key : callable, optional
        Optional priority key function to transform values into priority keys
        for sorting. By default, the values are not transformed.

    Returns
    -------
    list of up to n keys from the mapping

    """
    try:
        it = mapping.iteritems()
    except AttributeError:
        it = iter(mapping.items())
    pq = pqdict(key=key, precedes=gt)
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
    out = list(pq.popkeys())
    out.reverse()
    return out
