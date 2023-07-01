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

:copyright: (c) 2013-2023 by Nezar Abdennur.
:license: MIT, see LICENSE for more details.

"""
from collections.abc import MutableMapping
from operator import gt, lt
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from warnings import warn

__version__ = "1.3.0"
__all__ = ["pqdict", "nlargest", "nsmallest"]

DictInputs = Union[Mapping[Any, Any], Iterable[Tuple[Any, Any]]]
Tpqdict = TypeVar("Tpqdict", bound="pqdict")


class Node:
    __slots__ = ("key", "value", "prio")

    key: Any
    value: Any
    prio: Any

    def __init__(self, key: Any, value: Any, prio: Any) -> None:
        self.key = key
        self.value = value
        self.prio = prio

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.key}, {self.value}, {self.prio})"


class pqdict(MutableMapping):
    """
    A collection that maps hashable objects (keys) to priority-determining
    values. The mapping is mutable so items may be added, removed and have
    their priority level updated.

    The default behavior is that of a min-priority queue, i.e. the item with
    the *smallest* priority value is given *highest* priority. This behavior
    can be reversed by specifying ``reverse=True`` or by providing a custom
    precedence function via the ``precedes`` keyword argument. Alternatively,
    use the explicit :meth:`pqdict.minpq` or :meth:`pqdict.maxpq` class methods.

    Parameters
    ----------
    data : mapping or iterable, optional
        Input data, e.g. a dictionary or a sequence of items.
    key : callable, optional
        Optional priority key function to transform values into priority keys
        for comparison. By default, the values are used directly as priority
        keys and are not transformed.
    reverse : bool, optional [default: ``False``]
        If ``True``, *larger* priority keys give items *higher* priority.
        Default is ``False``.
    precedes : callable, optional [default: ``operator.lt``]
        Function that determines precedence of a pair of priority keys. The
        default comparator is ``operator.lt``, meaning *smaller* priority keys
        give items *higher* priority. The callable must have the form
        ``precedes(prio1, prio2) -> bool`` and return ``True`` if ``prio1``
        has higher priority than ``prio2``. Overrides ``reverse``.
    """

    _heap: List[Node]
    _position: Dict[Any, int]

    def __init__(
        self,
        data: Optional[DictInputs] = None,
        key: Optional[Callable[[Any], Any]] = None,
        reverse: bool = False,
        precedes: Callable[[Any, Any], bool] = lt,
    ) -> None:
        if reverse:
            if precedes == lt:
                precedes = gt
            else:
                raise ValueError("Got both `reverse=True` and a custom `precedes`.")

        if key is None or callable(key):
            self._keyfn = key
        else:
            raise ValueError(f"`key` function must be a callable; got {key}")

        if callable(precedes):
            self._precedes = precedes
        else:
            raise ValueError(f"`precedes` function must be a callable; got {precedes}")

        # The heap
        self._heap = []

        # The index
        self._position = {}

        if data is not None:
            self.update(data)

    @property
    def precedes(self) -> Callable[[Any, Any], bool]:
        """Priority key precedence function"""
        return self._precedes

    @property
    def keyfn(self) -> Callable[[Any], Any]:
        """Priority key function"""
        return self._keyfn if self._keyfn is not None else lambda x: x

    def __repr__(self) -> str:
        things = ", ".join([f"{node.key}: {node.value}" for node in self._heap])
        return f"{self.__class__.__name__}({things})"

    @classmethod
    def minpq(cls: Type[Tpqdict], *args: Any, **kwargs: Any) -> Tpqdict:
        """Create a pqdict with min-priority semantics: smallest is highest."""
        return cls(dict(*args, **kwargs), precedes=lt)

    @classmethod
    def maxpq(cls: Type[Tpqdict], *args: Any, **kwargs: Any) -> Tpqdict:
        """Create a pqdict with max-priority semantics: largest is highest."""
        return cls(dict(*args, **kwargs), precedes=gt)

    ############
    # dict API #
    ############
    __marker: object = object()
    # __eq__ = MutableMapping.__eq__
    # __ne__ = MutableMapping.__ne__
    # keys = MutableMapping.keys
    # values = MutableMapping.values
    # items = MutableMapping.items
    # get = MutableMapping.get
    # clear = MutableMapping.clear
    # update = MutableMapping.update
    # setdefault = MutableMapping.setdefault

    @classmethod
    def fromkeys(
        cls: Type[Tpqdict], iterable: Iterable, value: Any, **kwargs: Any
    ) -> Tpqdict:
        """
        Return a new pqdict mapping keys from an iterable to the same value.
        """
        return cls(((k, value) for k in iterable), **kwargs)

    def __len__(self) -> int:
        """
        Return number of items in the pqdict.
        """
        return len(self._heap)

    def __contains__(self, key: Any) -> bool:
        """
        Return ``True`` if key is in the pqdict.
        """
        return key in self._position

    def __iter__(self) -> Iterator[Any]:
        """
        Return an iterator over the keys of the pqdict. The order of iteration
        is arbitrary! Use ``popkeys`` to iterate over keys in priority order.
        """
        for node in self._heap:
            yield node.key

    def __getitem__(self, key: Any) -> Any:
        """
        Return the priority value of ``key``. Raises a ``KeyError`` if not in
        the pqdict.
        """
        return self._heap[self._position[key]].value  # raises KeyError

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Assign a priority value to ``key``. If ``key`` is already in the
        pqdict, its priority value is updated.
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
            heap.append(Node(key, value, prio))
            position[key] = n
            self._swim(n)
        else:
            # update
            prio = keygen(value) if keygen is not None else value
            heap[pos].value = value
            heap[pos].prio = prio
            self._reheapify(pos)

    def __delitem__(self, key: Any) -> None:
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

    def copy(self: Tpqdict) -> Tpqdict:
        """
        Return a shallow copy of a pqdict.
        """
        other = self.__class__(key=self._keyfn, precedes=self._precedes)
        other._position = self._position.copy()
        other._heap = [Node(node.key, node.value, node.prio) for node in self._heap]
        return other

    def pop(
        self,
        key: Any = __marker,
        default: Any = __marker,
    ) -> Any:
        """
        Hybrid pop method.

        Dictionary pop with ``key``:
        * If ``key`` is provided and is in the pqdict, remove the item and
          return its **value**.
        * If ``key`` is not in the pqdict, return ``default`` if provided,
          otherwise raise a ``KeyError``.

        Priority Queue pop without ``key``:
        * If ``key`` is not provided, remove the top item and return its
          **key**.
        * If the pqdict is empty, return ``default`` if provided, otherwise
          raise a ``KeyError``.
        """
        heap = self._heap
        position = self._position

        # pq semantics: remove and return top *key* (value is discarded)
        if key is self.__marker:
            if not heap:
                if default is self.__marker:
                    raise KeyError("pqdict is empty")
                else:
                    return default
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
    def top(self, default: Any = __marker) -> Any:
        """
        Return the key of the item with highest priority. If ``default`` is
        provided and pqdict is empty, then return``default``, otherwise raise
        ``KeyError``.
        """
        try:
            node = self._heap[0]
        except IndexError:
            if default is self.__marker:
                raise KeyError("pqdict is empty")
            else:
                return default
        return node.key

    def topvalue(self, default: Any = __marker) -> Any:
        """
        Return the value of the item with highest priority. If ``default`` is
        provided and pqdict is empty, then return``default``, otherwise raise
        ``KeyError``.
        """
        try:
            node = self._heap[0]
        except IndexError:
            if default is self.__marker:
                raise KeyError("pqdict is empty")
            else:
                return default
        return node.value

    def topitem(self) -> Tuple[Any, Any]:
        """
        Return the item with highest priority. Raises ``KeyError`` if pqdict is
        empty.
        """
        try:
            node = self._heap[0]
        except IndexError:
            raise KeyError("pqdict is empty")
        return node.key, node.value

    def popvalue(self, default: Any = __marker) -> Any:
        """
        Remove and return the value of the item with highest priority. If
        ``default`` is provided and pqdict is empty, then return``default``,
        otherwise raise ``KeyError``.
        """
        heap = self._heap
        position = self._position

        if not heap:
            if default is self.__marker:
                raise KeyError("pqdict is empty")
            else:
                return default

        value = heap[0].value
        del self[heap[0].key]
        return value

    def popitem(self) -> Tuple[Any, Any]:
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

    def additem(self, key: Any, value: Any) -> None:
        """
        Add a new item. Raises ``KeyError`` if key is already in the pqdict.
        """
        if key in self._position:
            raise KeyError(f"{key} is already in the queue")
        self[key] = value

    def pushpopitem(self, key: Any, value: Any) -> Tuple[Any, Any]:
        """
        Equivalent to inserting a new item followed by removing the top
        priority item, but faster. Raises ``KeyError`` if the new key is
        already in the pqdict.
        """
        heap = self._heap
        position = self._position
        precedes = self._precedes
        prio = self._keyfn(value) if self._keyfn else value
        node = Node(key, value, prio)
        if key in self:
            raise KeyError(f"{key} is already in the queue")
        if heap and precedes(heap[0].prio, node.prio):
            node, heap[0] = heap[0], node
            position[key] = 0
            del position[node.key]
            self._sink(0)
        return node.key, node.value

    def updateitem(self, key: Any, new_val: Any) -> None:
        """
        Update the priority value of an existing item. Raises ``KeyError`` if
        key is not in the pqdict.
        """
        if key not in self._position:
            raise KeyError(key)
        self[key] = new_val

    def replace_key(self, key: Any, new_key: Any) -> None:
        """
        Replace the key of an existing heap node in place. Raises ``KeyError``
        if the key to replace does not exist or if the new key is already in
        the pqdict.
        """
        heap = self._heap
        position = self._position
        if new_key in self:
            raise KeyError(f"{new_key} is already in the queue")
        pos = position.pop(key)  # raises appropriate KeyError
        position[new_key] = pos
        heap[pos].key = new_key

    def swap_priority(self, key1: Any, key2: Any) -> None:
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

    def popkeys(self) -> Iterator[Any]:
        """
        Remove items, returning keys in descending order of priority rank.
        """
        try:
            while True:
                yield self.popitem()[0]
        except KeyError:
            return

    def popvalues(self) -> Iterator[Any]:
        """
        Remove items, returning values in descending order of priority rank.
        """
        try:
            while True:
                yield self.popitem()[1]
        except KeyError:
            return

    def popitems(self) -> Iterator[Tuple[Any, Any]]:
        """
        Remove and return items in descending order of priority rank.
        """
        try:
            while True:
                yield self.popitem()
        except KeyError:
            return

    def heapify(self, key: Any = __marker) -> None:
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

    ###################
    # Heap algorithms #
    ###################
    # The names of the heap operations in `heapq` (sift up/down) refer to the
    # motion of the nodes being compared to, rather than the node being
    # operated on as is usually done in textbooks (i.e. bubble down/up,
    # instead). Here I use the sink/swim nomenclature from
    # http://algs4.cs.princeton.edu/24pq/. The way I like to think of it, an
    # item that is too "heavy" (low-priority) should sink down the tree, while
    # one that is too "light" should float or swim up.
    def _reheapify(self, pos: int) -> None:
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

    def _sink(self, top: int = 0) -> None:
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

    def _swim(self, pos: int, top: int = 0) -> None:
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


def minpq(*args: Any, **kwargs: Any) -> pqdict:
    warn(
        "The `minpq` module function is deprecated and will be removed in v1.4. "
        "Use the classmethod `pqdict.minpq()` instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return pqdict(dict(*args, **kwargs), precedes=lt)


def maxpq(*args: Any, **kwargs: Any) -> pqdict:
    warn(
        "The `maxpq` module function is deprecated and will be removed in v1.4. "
        "Use the classmethod `pqdict.maxpq()` instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return pqdict(dict(*args, **kwargs), precedes=gt)


#############
# Functions #
#############


def nlargest(n: int, mapping: Mapping, key: Optional[Callable[[Any], Any]] = None):
    """
    Takes a mapping and returns the n keys associated with the largest values
    in descending order. If the mapping has fewer than n items, all its keys
    are returned.

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
    list of up to n keys from the mapping associated with the largest values

    Notes
    -----
    This function is equivalent to:

    >>> [item[0] for item in heapq.nlargest(n, mapping.items(), lambda x: x[1])]
    """
    it = iter(mapping.items())
    pq = pqdict(key=key, precedes=lt)
    try:
        for _ in range(n):
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


def nsmallest(n: int, mapping: Mapping, key: Optional[Callable[[Any], Any]] = None):
    """
    Takes a mapping and returns the n keys associated with the smallest values
    in ascending order. If the mapping has fewer than n items, all its keys are
    returned.

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
    list of up to n keys from the mapping associated with the smallest values

    Notes
    -----
    This function is equivalent to:

    >>> [item[0] for item in heapq.nsmallest(n, mapping.items(), lambda x: x[1])]
    """
    it = iter(mapping.items())
    pq = pqdict(key=key, precedes=gt)
    try:
        for _ in range(n):
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
