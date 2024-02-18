"""Priority Queue Dictionary (pqdict).

A Pythonic indexed priority queue.

A dict-like heap queue to prioritize hashable objects while providing random
access and updatable priorities. Inspired by the ``heapq`` standard library
module, which was written by Kevin O'Connor and augmented by Tim Peters and
Raymond Hettinger.

The priority queue is implemented as a binary heap of (key, priority value)
elements, which supports:

- O(1) search for the item with highest priority

- O(log n) removal of the item with highest priority

- O(log n) insertion of a new item

Additionally, an index maps each key to its element's location in the heap
and is kept up to date as the heap is manipulated. As a result, pqdict also
supports:

- O(1) lookup of any item by key

- O(log n) removal of any item

- O(log n) updating of any item's priority level

Documentation at <http://pqdict.readthedocs.org/>.

:copyright: (c) 2012-2024 by Nezar Abdennur.
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
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

__version__ = "1.4.0"
__all__ = ["pqdict", "nlargest", "nsmallest"]

DictInputs = Union[Mapping[Any, Any], Iterable[Tuple[Any, Any]]]
Tpqdict = TypeVar("Tpqdict", bound="pqdict")
PrioKeyFn = Callable[[Any], Any]
PrecedesFn = Callable[[Any, Any], bool]


class Empty(KeyError):
    # Why specialize KeyError? Why not reuse queue.Empty?
    # The Mapping protocol expects KeyError when popping from an empty map.
    # This lets us distinguish between a key not in the map and an empty map.
    pass


class Node(NamedTuple):
    key: Any
    value: Any
    prio: Any


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


def _sink(
    heap: List[Node], position: Dict[Any, int], precedes: PrecedesFn, top: int = 0
) -> None:
    # "Sink-to-the-bottom-then-swim" algorithm (Floyd, 1964)
    # Tends to reduce the number of comparisons when inserting "heavy"
    # items at the top, e.g. during a heap pop. See heapq for more details.
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
    _swim(heap, position, precedes, pos, top)


def _swim(
    heap: List[Node],
    position: Dict[Any, int],
    precedes: PrecedesFn,
    pos: int,
    top: int = 0,
) -> None:
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


def heapify(heap: List[Node], position: Dict[Any, int], precedes: PrecedesFn) -> None:
    n = len(heap)
    # No need to look at any leaf nodes.
    for pos in reversed(range(n // 2)):
        _sink(heap, position, precedes, pos)


def heaprepair(
    heap: List[Node], position: Dict[Any, int], precedes: PrecedesFn, pos: int
) -> None:
    # Repair the position of a modified node.
    # Bubble up or down depending on values of parent and children.
    parent_pos = (pos - 1) >> 1
    child_pos = 2 * pos + 1
    if parent_pos > -1 and precedes(heap[pos].prio, heap[parent_pos].prio):
        _swim(heap, position, precedes, pos)
    elif child_pos < len(heap):
        other_pos = child_pos + 1
        if other_pos < len(heap) and not precedes(
            heap[child_pos].prio, heap[other_pos].prio
        ):
            child_pos = other_pos
        if precedes(heap[child_pos].prio, heap[pos].prio):
            _sink(heap, position, precedes, pos)


def heappop(
    heap: List[Node], position: Dict[Any, int], precedes: PrecedesFn, pos: int = 0
) -> Node:
    # Take the very last node and place it in the vacated spot. Let it
    # sink or swim until it reaches its new resting place.
    node_to_replace = heap[pos]
    last = heap.pop()
    if last is not node_to_replace:
        heap[pos] = last
        position[last.key] = pos
        heaprepair(heap, position, precedes, pos)
    del position[node_to_replace.key]
    return node_to_replace


def heappush(
    heap: List[Node], position: Dict[Any, int], precedes: PrecedesFn, node: Node
) -> None:
    n = len(heap)
    heap.append(node)
    position[node.key] = n
    _swim(heap, position, precedes, n)


def heapupdate(
    heap: List[Node], position: Dict[Any, int], precedes: PrecedesFn, node: Node
) -> None:
    pos = position[node.key]
    heap[pos] = node
    heaprepair(heap, position, precedes, pos)


def heappushpop(
    heap: List[Node], position: Dict[Any, int], precedes: PrecedesFn, node: Node
) -> Node:
    key = node.key
    if heap and precedes(heap[0].prio, node.prio):
        node, heap[0] = heap[0], node
        position[key] = 0
        del position[node.key]
        _sink(heap, position, precedes, 0)
    return node


class pqdict(MutableMapping):
    """A mutable dict/priority queue that maps hashable keys to priority values.

    As a priority queue, items can be added and the top-priority item can be
    viewed or dequeued. In addition, arbitrary items may be retrieved, removed,
    and have their priorities updated by key.
    """

    _heap: List[Node]
    _position: Dict[Any, int]

    def __init__(
        self,
        data: Optional[DictInputs] = None,
        key: Optional[PrioKeyFn] = None,
        reverse: bool = False,
        precedes: PrecedesFn = lt,
    ):
        """Create a new priority queue dictionary.

        Parameters
        ----------
        data : mapping or iterable, optional
            Input data, e.g. a dictionary or a sequence of items.
        key : callable, optional
            Optional priority key function to transform values into priority
            keys for comparison. By default, the values are used directly as
            priority keys and are not transformed.
        reverse : bool, optional [default: ``False``]
            If ``True``, *larger* priority keys give items *higher* priority.
            Default is ``False``.
        precedes : callable, optional [default: ``operator.lt``]
            Function that determines precedence of a pair of priority keys. The
            default comparator is ``operator.lt``, meaning *smaller* priority
            keys give items *higher* priority. The callable must have the form
            ``precedes(prio1, prio2) -> bool`` and return ``True`` if ``prio1``
            has higher priority than ``prio2``. Overrides ``reverse``.

        Notes
        -----
        The default behavior is that of a **min**-priority queue, i.e. the item
        with the *smallest* value is given *highest* priority. This behavior
        can be reversed by specifying ``reverse=True`` or by providing a custom
        precedence function via the ``precedes`` keyword argument.
        Alternatively, use the explicit :meth:`pqdict.minpq` or
        :meth:`pqdict.maxpq` class methods.

        """
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
    def precedes(self) -> PrecedesFn:
        """Priority key precedence function."""
        return self._precedes

    @property
    def keyfn(self) -> PrioKeyFn:
        """Priority key function."""
        return self._keyfn if self._keyfn is not None else lambda x: x

    def __repr__(self) -> str:
        """Return a string representation of the pqdict."""
        things = ", ".join([f"{node.key}: {node.value}" for node in self._heap])
        return f"{self.__class__.__name__}({things})"

    @classmethod
    def minpq(cls: Type[Tpqdict], *args: Any, **kwargs: Any) -> Tpqdict:
        """Create a pqdict with min-priority semantics: smallest value is highest.

        * ``pqdict.minpq()`` -> new empty pqdict with min-priority semantics
        * ``pqdict.minpq(mapping)`` -> new minpq initialized from a mapping
        * ``pqdict.minpq(iterable)`` -> new minpq initialized from an iterable of pairs
        * ``pqdict.minpq(**kwargs)`` -> new minpq initialized with name=value pairs
        """
        return cls(dict(*args, **kwargs), precedes=lt)

    @classmethod
    def maxpq(cls: Type[Tpqdict], *args: Any, **kwargs: Any) -> Tpqdict:
        """Create a pqdict with max-priority semantics: largest value is highest.

        * ``pqdict.maxpq()`` -> new empty pqdict with max-priority semantics
        * ``pqdict.maxpq(mapping)`` -> new maxpq initialized from a mapping
        * ``pqdict.maxpq(iterable)`` -> new maxpq initialized from an iterable of pairs
        * ``pqdict.maxpq(**kwargs)`` -> new maxpq initialized with name=value pairs
        """
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
        """Return a new pqdict mapping keys from an iterable to the same value."""
        return cls(((k, value) for k in iterable), **kwargs)

    def __len__(self) -> int:
        """Return number of items in the pqdict."""
        return len(self._heap)

    def __contains__(self, key: Any) -> bool:
        """Return ``True`` if key is in the pqdict."""
        return key in self._position

    def __iter__(self) -> Iterator[Any]:
        """Return an iterator over the keys of the pqdict.

        The order of iteration is arbitrary! Use ``popkeys`` to iterate over
        keys in priority order.
        """
        for node in self._heap:
            yield node.key

    def __getitem__(self, key: Any) -> Any:
        """Return the priority value of ``key``.

        Raises a ``KeyError`` if not in the pqdict.
        """
        return self._heap[self._position[key]].value  # raises KeyError

    def __setitem__(self, key: Any, value: Any) -> None:
        """Assign a priority value to ``key``.

        If ``key`` is already in the pqdict, its priority value is updated.
        """
        prio = self._keyfn(value) if self._keyfn else value
        node = Node(key, value, prio)
        if key in self._position:
            heapupdate(self._heap, self._position, self._precedes, node)
        else:
            heappush(self._heap, self._position, self._precedes, node)

    def __delitem__(self, key: Any) -> None:
        """Remove item.

        Raises a ``KeyError`` if key is not in the pqdict.
        """
        if key not in self._position:
            raise KeyError(key)
        heappop(self._heap, self._position, self._precedes, self._position[key])

    def copy(self: Tpqdict) -> Tpqdict:
        """Return a shallow copy of a pqdict."""
        other = self.__class__(key=self._keyfn, precedes=self._precedes)
        other._position = self._position.copy()
        other._heap = self._heap[:]
        return other

    def pop(
        self,
        key: Any = __marker,
        default: Any = __marker,
    ) -> Any:
        """Hybrid pop method.

        With ``key``, perform a dictionary pop:

        * If ``key`` is in the pqdict, remove the item and return its
          **value**.
        * If ``key`` is not in the pqdict, return ``default`` if provided,
          otherwise raise a ``KeyError``.

        Without ``key``, perform a priority queue pop:

        * Remove the top item and return its **key**.
        * If the pqdict is empty, return ``default`` if provided, otherwise
          raise ``Empty``.
        """
        # pq semantics: remove and return top *key* (value is discarded)
        if key is self.__marker:
            if self._heap:
                return heappop(self._heap, self._position, self._precedes).key
            elif default is self.__marker:
                raise Empty("pqdict is empty")
            else:
                return default
        # dict semantics: remove and return *value* mapped from key
        elif key in self._position:
            return heappop(
                self._heap, self._position, self._precedes, self._position[key]
            ).value
        elif default is self.__marker:
            raise KeyError(key)
        else:
            return default

    ######################
    # Priority Queue API #
    ######################
    def top(self, default: Any = __marker) -> Any:
        """Return the key of the item with highest priority.

        If ``default`` is provided and pqdict is empty, then return ``default``,
        otherwise raise ``Empty``.
        """
        if self._heap:
            return self._heap[0].key
        elif default is self.__marker:
            raise Empty("pqdict is empty")
        else:
            return default

    def topvalue(self, default: Any = __marker) -> Any:
        """Return the value of the item with highest priority.

        If ``default`` is provided and pqdict is empty, then return ``default``,
        otherwise raise ``Empty``.
        """
        if self._heap:
            return self._heap[0].value
        elif default is self.__marker:
            raise Empty("pqdict is empty")
        else:
            return default

    def topitem(self, default: Any = __marker) -> Tuple[Any, Any]:
        """Return the item with highest priority.

        Raises ``Empty`` if pqdict is empty.
        """
        if self._heap:
            node = self._heap[0]
            return node.key, node.value
        elif default is self.__marker:
            raise Empty("pqdict is empty")
        else:
            return default

    def popvalue(self, default: Any = __marker) -> Any:
        """Remove and return the value of the item with highest priority.

        If ``default`` is provided and pqdict is empty, then return ``default``,
        otherwise raise ``Empty``.
        """
        if self._heap:
            return heappop(self._heap, self._position, self._precedes).value
        elif default is self.__marker:
            raise Empty("pqdict is empty")
        else:
            return default

    def popitem(self, default: Any = __marker) -> Tuple[Any, Any]:
        """Remove and return the item with highest priority.

        Raises ``Empty`` if pqdict is empty.
        """
        if self._heap:
            node = heappop(self._heap, self._position, self._precedes)
            return node.key, node.value
        elif default is self.__marker:
            raise Empty("pqdict is empty")
        else:
            return default

    def additem(self, key: Any, value: Any) -> None:
        """Add a new item.

        Raises ``KeyError`` if key is already in the pqdict.
        """
        if key in self._position:
            raise KeyError(f"{key} is already in the queue")
        prio = self._keyfn(value) if self._keyfn else value
        node = Node(key, value, prio)
        heappush(self._heap, self._position, self._precedes, node)

    def updateitem(self, key: Any, new_val: Any) -> None:
        """Update the priority value of an existing item.

        Raises ``KeyError`` if key is not in the pqdict.
        """
        if key not in self._position:
            raise KeyError(key)
        prio = self._keyfn(new_val) if self._keyfn else new_val
        node = Node(key, new_val, prio)
        heapupdate(self._heap, self._position, self._precedes, node)

    def pushpopitem(self, key: Any, value: Any) -> Tuple[Any, Any]:
        """Insert a new item and return the top-priority item.

        Equivalent to inserting a new item followed by removing the top
        priority item, but faster. Raises ``KeyError`` if the new key is
        already in the pqdict.
        """
        if key in self._position:
            raise KeyError(f"{key} is already in the queue")
        prio = self._keyfn(value) if self._keyfn else value
        node = heappushpop(
            self._heap, self._position, self._precedes, Node(key, value, prio)
        )
        return node.key, node.value

    def replace_key(self, key: Any, new_key: Any) -> None:
        """Replace the key of an existing heap node in place.

        Raises ``KeyError`` if the key to replace does not exist or if the new
        key is already in the pqdict.
        """
        if new_key in self._position:
            raise KeyError(f"{new_key} is already in the queue")
        pos = self._position.pop(key)  # raises appropriate KeyError
        self._position[new_key] = pos
        node = self._heap[pos]
        self._heap[pos] = Node(new_key, node.value, node.prio)

    def swap_priority(self, key1: Any, key2: Any) -> None:
        """Fast way to swap the priority level of two items in the pqdict.

        Raises ``KeyError`` if either key does not exist.
        """
        heap = self._heap
        position = self._position
        if key1 not in position:
            raise KeyError(key1)
        if key2 not in position:
            raise KeyError(key2)
        pos1, pos2 = position[key1], position[key2]
        node1, node2 = heap[pos1], heap[pos2]
        heap[pos1] = Node(key2, node1.value, node1.prio)
        heap[pos2] = Node(key1, node2.value, node2.prio)
        position[key1], position[key2] = pos2, pos1

    def popkeys(self) -> Iterator[Any]:
        """Remove items, returning keys in descending order of priority rank."""
        try:
            while True:
                yield self.pop()
        except Empty:
            return

    def popvalues(self) -> Iterator[Any]:
        """Remove items, returning values in descending order of priority rank."""
        try:
            while True:
                yield self.popvalue()
        except Empty:
            return

    def popitems(self) -> Iterator[Tuple[Any, Any]]:
        """Remove and return items in descending order of priority rank."""
        try:
            while True:
                yield self.popitem()
        except Empty:
            return

    def heapify(self, key: Any = __marker) -> None:
        """Repair a broken heap.

        If a change in a single, mutable value caused the break, you can
        provide ``key`` to repair the heap by relocating that item.
        """
        if key is self.__marker:
            heapify(self._heap, self._position, self._precedes)
        else:
            if key not in self._position:
                raise KeyError(key)
            heaprepair(self._heap, self._position, self._precedes, self._position[key])


#############
# Functions #
#############


def nlargest(n: int, mapping: Mapping, key: Optional[PrioKeyFn] = None):
    """Return the n keys associated with the largest values in a mapping.

    Takes a mapping and returns the n keys associated with the largest values
    in descending order. If the mapping has fewer than n items, all its keys
    are returned.

    Parameters
    ----------
    n : int
        The number of keys associated with the largest values
        in descending order
    mapping : Mapping
        A dict-like object
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


def nsmallest(n: int, mapping: Mapping, key: Optional[PrioKeyFn] = None):
    """Return the n keys associated with the smallest values in a mapping.

    Takes a mapping and returns the n keys associated with the smallest values
    in ascending order. If the mapping has fewer than n items, all its keys are
    returned.

    Parameters
    ----------
    n : int
        The number of keys associated with the smallest values
        in ascending order
    mapping : Mapping
        A dict-like object
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
