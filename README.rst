Priority Queue Dictionary (pqdict)
==================================

A priority queue dictionary maps hashable objects (keys) to priority-determining values. It provides a hybrid dictionary/priority queue API. 

Works with Python 2.7+ and 3.3+.

.. image:: https://travis-ci.org/nvictus/priority-queue-dictionary.png?branch=master   
    :target: https://travis-ci.org/nvictus/priority-queue-dictionary
    :alt: CI Build State

.. image:: https://img.shields.io/pypi/v/pqdict.svg
    :target: https://pypi.python.org/pypi/pqdict

.. image:: https://img.shields.io/pypi/dm/pqdict.svg
        :target: https://pypi.python.org/pypi/pqdict

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


Documentation
-------------

Documentation is available at http://pqdict.readthedocs.org/en/latest/.


License 
-------

This module is released under the MIT license. The augmented heap implementation was adapted from the ``heapq`` module in the Python standard library, which was written by Kevin O'Connor and augmented by Tim Peters and Raymond Hettinger.
