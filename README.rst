Priority Queue Dictionary (pqdict)
==================================

``pqdict`` provides an indexed priority queue data structure implemented in pure Python as a dict-like class. ``pqdict.PQDict`` instances map hashable dictionary keys to comparable priority keys and operate like regular Python dictionaries but with added priority queue functionality.

What is an "indexed" priority queue?
------------------------------------

A `priority queue <http://en.wikipedia.org/wiki/Priority_queue>`__ is an
abstract data structure that allows you to serve or retrieve items in a
prioritized fashion. A vanilla priority queue lets you insert elements with priorities, and remove or peek at the top priority element. 

An enhancement to the basic priority queue interface is to let you randomly access, insert, remove and/or alter the priority of any existing element in the queue. An *indexed* priority queue does these operations efficiently.

The queue is implemented as a binary heap (using a python list), which supports the standard:

-  O(1) access to the top priority element

-  O(log n) removal of the top priority element

-  O(log n) insertion of a new element

In addition, an internal dictionary or "index" maps elements to their
position in the heap. This index is synchronized with the heap as the
heap is manipulated. As a result, ``PQDict`` also supports:

-  O(1) lookup of an arbitrary element's priority key

-  O(log n) removal of an arbitrary element

-  O(log n) updating of an arbitrary element's priority key

Why would I want something like that?
-------------------------------------

Indexed priority queues can be used to drive simulations, priority schedulers, optimization algorithms, multiway merging of streams of prioritized data, and other applications where priorities of already enqueued items may frequently change.

A simple and well-known application for mutable priorities is
`Dijkstra's algorithm <https://gist.github.com/nvictus/6260717>`__. Another use case example from my experience is to speed up simulations of stochastic processes such as chemical reaction networks.

Usage
--------

By default, ``PQDict`` uses a min-heap, meaning **smaller** priority
keys have **higher** priority. Use ``PQDict.maxpq()`` to create a
max-heap priority queue.

.. code:: python

    from pqdict import PQDict

    # same input signature as dict()
    pq = PQDict(a=3, b=5, c=8)
    pq = PQDict(zip(['a','b','c'], [3, 5, 8]))
    pq = PQDict({'a':3, 'b':5, 'c':8})          

    # add/update items this way...
    pq.additem('d', 15)
    pq.updateitem('c', 1)

    # ...or this way
    pq['d'] = 6.5
    pq['e'] = 2
    pq['f'] = -5

    # read an element's priority
    print 'f' in pq          # True
    print pq['f']            # -5               
    
    # remove an element and get its priority key
    pkey = pq.pop('f')        
    print 'f' in pq          # False             
    print pq.get('f', None)  # None

    # or just delete an element
    del pq['e']

    # peek at the top priority item
    print pq.peek()          # ('c', 1)

    # let's do a manual heapsort
    print pq.popitem()       # ('c', 1)
    print pq.popitem()       # ('a', 3)
    print pq.popitem()       # ('b', 5)
    print pq.popitem()       # ('d', 6.5)

    # and we're empty!
    pq.popitem()             # KeyError

**Regular iteration** has no prescribed order and is non-destructive.

.. code:: python

    queue = PQDict({'Alice':1, 'Bob':2}) 
    for customer in queue:     
        serve(customer) # Bob may be served before Alice!

This also applies to ``pq.keys()``, ``pq.values()``, ``pq.items()`` and using ``iter()``.

.. code:: python 

    >>> PQDict({'a': 1, 'b': 2, 'c': 3, 'd': 4}).keys() 
    ['a', 'c', 'b', 'd']

**Destructive iteration** methods return generators that pop items out of the heap, which amounts to performing a heapsort:

.. code:: python 

    for customer in queue.iterkeys():     
        serve(customer) # Customer satisfaction guaranteed :) 
    # queue is now empty

The destructive iterators are ``pq.iterkeys()``, ``pq.itervalues()``, and ``pq.iteritems()``.

There is also a convenience function to sort a dictionary-like object by value using a ``PQDict``. It is non-destructive and returns a sorted list of dictionary items. 

.. code:: python 

    from pqdict import sort_by_value

    billionaires = {'Bill Gates': 72.7, 'Warren Buffett': 60.0, ...}
    top10_richest = sort_by_value(billionaires, reverse=True)[:10]

License 
-------

This module was written by Nezar Abdennur and is released under the MIT license. The augmented heap implementation was adapted from the ``heapq`` module in the Python standard library, which was written by Kevin O'Connor and augmented by Tim Peters and Raymond Hettinger.
