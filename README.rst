Priority Queue Dictionary (pqdict)
==================================

``pqdict`` provides a pure Python indexed priority queue data structure with a dict-like interface. ``pqdict.PQDict`` instances map hashable *dictionary keys* to rank-determining *priority keys*.

.. image:: https://travis-ci.org/nvictus/priority-queue-dictionary.png?branch=master   
    :target: https://travis-ci.org/nvictus/priority-queue-dictionary
    :alt: CI Build State

.. image:: https://pypip.in/v/pqdict/badge.png
    :target: http://pythonhosted.org/pqdict
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/pqdict/badge.png
    :target: https://pypi.python.org/pypi/pqdict/
    :alt: Number of PyPI downloads


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

Indexed priority queues can be used to drive simulations, priority schedulers, and optimization algorithms, merge of streams of prioritized data, and other applications where priorities of already enqueued items may frequently change.

Usage
--------

By default, ``PQDict`` uses a min-heap, meaning **smaller** priority
keys give an item **higher** priority. Use ``PQDict.maxpq()`` to create a
max-heap priority queue.

.. code:: python

    from pqdict import PQDict

    # same input signature as dict
    pq = PQDict(a=3, b=5, c=8)
    pq = PQDict(zip(['a','b','c'], [3, 5, 8]))
    pq = PQDict({'a':3, 'b':5, 'c':8})          

    # add/update items
    pq['d'] = 6.5
    pq['e'] = 2
    pq['f'] = -5

    # or more stringently
    pq.additem('d', 15)
    pq.updateitem('c', 1)
    pq.additem('c', 4)       # KeyError
    pq.updateitem('x', 4)    # KeyError

    # get an element's priority key
    print 'f' in pq          # True
    print pq['f']            # -5

    # remove elements
    print pq.pop('f')        # -5
    print 'f' in pq          # False
    del pq['e']
    print pq.get('e', None)  # None

    # peek at the top priority item
    print pq.top()           # 'c'
    print pq.topitem()       # ('c', 1)

    # Now, let's do a manual heapsort...
    print pq.pop()           # 'c'
    print pq.popitem()       # ('a', 3)
    print pq.popitem()       # ('b', 5)
    print pq.popitem()       # ('d', 6.5)

    # and we're empty!
    pq.popitem()             # KeyError

.. note::
    **Regular iteration** is **NOT** sorted! However, regular iteration methods are non-destructive: they don't affect the heap. This applies to ``pq.keys()``, ``pq.values()``, ``pq.items()`` and using ``iter()``:

.. code:: python

    queue = PQDict({'Alice':1, 'Bob':2}) 
    for customer in queue:     
        serve(customer) # Bob may be served before Alice!

.. code:: python 

    >>> PQDict({'a': 1, 'b': 2, 'c': 3, 'd': 4}).keys() 
    ['a', 'c', 'b', 'd']

.. note::
    **Heapsort iteration** is sorted, but destructive. Heapsort iteration methods return generators that pop items out of the heap, which amounts to performing a heapsort. The heapsort iterators are ``pq.iterkeys()``, ``pq.itervalues()``, and ``pq.iteritems()``:

.. code:: python 

    for customer in queue.iterkeys():     
        serve(customer) # Customer satisfaction guaranteed :) 
    # queue is now empty


Module functions
----------------
Some functions are provided in addition to the ``PQDict`` class.

``pqdict.sort_by_value`` is a convenience function that returns a heapsort iterator over the items of a mapping. Generator equivalent of ``sorted(mapping.items(), key=itemgetter(1), reverse=reverse)``.


``pqdict.nsmallest`` and ``pqdict.nlargest`` work just like the same functions in ``heapq`` but act on dictionaries and dict-like objects instead of sequences, sorting by value:

.. code:: python 

    from pqdict import nlargest

    billionaires = {'Bill Gates': 72.7, 'Warren Buffett': 60.0, ...}
    top10_richest = nlargest(10, billionaires)


``pqdict.consume`` consumes the items from multiple priority queue dictionaries into a single sorted output stream:

.. code:: python

    pqA = PQDict(parse_feed(urlA))
    pqB = PQDict(parse_feed(urlB))
    pqC = PQDict(parse_feed(urlC))

    aggregator = pqdict.consume(pqA, pqB, pqC)

    for entry, date in aggregator:
        print '%s was posted on %s' % (entry, date)
    ...


License 
-------

This module is released under the MIT license. The augmented heap implementation was adapted from the ``heapq`` module in the Python standard library, which was written by Kevin O'Connor and augmented by Tim Peters and Raymond Hettinger.


.. image:: https://d2weczhvl823v0.cloudfront.net/nvictus/priority-queue-dictionary/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

