Quickstart
==========

What is an "indexed" priority queue?
------------------------------------

A `priority queue <http://en.wikipedia.org/wiki/Priority_queue>`__ allows you to serve or retrieve items in a prioritized fashion. A priority queue supports inserting elements with priorities, and removing or peeking at the top priority element. The vanilla priority queue interface can be extended to support random access, insertion, removal and changing the priority of any element in the queue. An *indexed* priority queue does these latter operations efficiently.

The priority queue is implemented as a binary heap of (key, priority value) pairs, which supports:

* O(1) search for the item with highest priority

* O(log n) removal of the item with highest priority

* O(log n) insertion of a new item

An internal index maps elements to their location in the heap and is kept up to date as the heap is manipulated. As a result, pqdict also supports:

* O(1) lookup of any item by key

* O(log n) removal of any item          

* O(log n) updating of any item's priority level

Indexed priority queues are useful in applications where priorities of already enqueued items may frequently change (e.g., schedulers, optimization algorithms, simulations, etc.).


Usage
-----
The default heap is a min-heap, meaning **smaller** values give an item **higher** priority.

.. code-block:: python

    >>> from pqdict import pqdict
    >>> pq = pqdict({'a':3, 'b':5, 'c':8})
    >>> list(pq.popkeys())
    ['a', 'b', 'c']

To create a max-heap instead (**larger** values give **higher** priority), pass in the option ``reverse=True``.

.. code-block:: python

    >>> from pqdict import pqdict
    >>> pq = pqdict({'a':3, 'b':5, 'c':8}, reverse=True)
    >>> list(pq.popkeys())
    ['c', 'b', 'a']

Alternatively, you can use the constructors :meth:`~pqdict.pqdict.minpq` and :meth:`~pqdict.pqdict.maxpq`.

.. code-block:: python

    >>> from pqdict import pqdict
    >>> pq = pqdict.minpq(a=3, b=5, c=8)

By default, items are ordered by **value**. Analogous to the built-in ``sorted()``, you can provide a **priority key function** to transform the values for sorting.

.. code-block:: python
    
    >>> from pqdict import pqdict
    >>> pq = pqdict({'a':(10, 3), 'b':(8, 5), 'c':(3, 8)}, key=lambda x: x[1])
    >>> list(pq.popkeys())
    ['a', 'b', 'c']

Views and regular iteration don't affect the heap, but the output is **unsorted**. This applies to ``pq.keys()``, ``pq.values()``, ``pq.items()`` and using ``iter()`` (e.g., in a for loop).

.. code-block:: python

    queue = pqdict({'Alice':1, 'Bob':2}) 
    for customer in queue:     
        serve(customer) # Bob may be served before Alice!

.. code-block:: python 

    >>> list(pqdict({'a': 1, 'c': 3, 'b': 2, 'd': 4}).keys())
    ['a', 'c', 'b', 'd']


"Heapsort iterators" output data in **descending order of priority** by removing items from the collection. The following methods return heapsort iterators: ``pq.popkeys()``, ``pq.popvalues()``, and ``pq.popitems()``.

.. code-block:: python 

    for customer in queue.popkeys():     
        serve(customer) # Customer satisfaction guaranteed :) 
    # queue is now empty

.. code-block:: python 

    >>> list(pqdict({'a': 1, 'c': 3, 'b': 2, 'd': 4}).popkeys())
    ['a', 'b', 'c', 'd']


:class:`~pqdict.pqdict` supports all Python dictionary methods...

.. code-block:: python

    >>> from pqdict import pqdict
    >>> pq = pqdict({'a':3, 'b':5, 'c':8})
    >>> pq['d'] = 6.5
    >>> pq['e'] = 2
    >>> pq['f'] = -5
    >>> 'f' in pq
    True
    >>> pq['f']
    -5
    >>> pq.pop('f')
    -5
    >>> 'f' in pq
    False
    >>> del pq['e']
    >>> pq.get('e', None)
    None

\...and exposes a priority queue API.

.. code-block:: python

    >>> pq.top()
    'c'
    >>> pq.topvalue()
    1
    >>> pq.topitem()
    ('c', 1)
    # manual heapsort...
    >>> pq.pop()  # no args
    'c'
    >>> pq.popitem()
    ('a', 3)
    >>> pq.popitem()
    ('b', 5)
    >>> pq.popitem()
    ('d', 6.5)
    >>> pq.popitem()  # ...and we're empty!
    KeyError


.. warning:: 
    **Value mutability**. If you use mutable objects as values in a :class:`~pqdict.pqdict`, changes to the state of those objects can break the priority queue. If this does happen, the data structure can be repaired by calling ``pq.heapify()``. (But you probably shouldn't be using mutable values in the first place.)

.. note::
    **Custom precedence function**. The only difference between a min-pq and max-pq is that precedence of items is determined by comparing priority keys with the builtin ``<`` and ``>`` operators, respectively. If you would like to further customize the way items are prioritized, you can pass a boolean function ``precedes(pkey1, pkey2)`` to the initializer.

The module functions :func:`~pqdict.nsmallest` and :func:`~pqdict.nlargest` work like the same functions in :mod:`heapq` but act on mappings instead of sequences, sorting by value:

.. code-block:: python

    >>> from pqdict import nlargest
    >>> billionaires = {'Bill Gates': 72.7, 'Warren Buffett': 60.0, ...}
    >>> top5_names = nlargest(5, billionaires)


License 
-------

This module is released under the MIT license. The augmented heap implementation was adapted from the :mod:`heapq` module in the Python standard library, which was written by Kevin O'Connor and augmented by Tim Peters and Raymond Hettinger.


Documentation
-------------

Documentation is available at http://pqdict.readthedocs.org/en/latest/.
