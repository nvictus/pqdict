API Reference
=============

.. toctree::
   :maxdepth: 2

.. currentmodule:: pqdict


pqdict class
------------
.. autoclass:: pqdict
    :no-members:

    .. automethod:: fromkeys

    .. automethod:: heapify([key])

    |

    **Properties**

    .. autoattribute:: keyfn

    .. autoattribute:: precedes

    |

    **Dictionary API**

    These do as expected. See :py:class:`dict` for more details.

    .. method:: len(pq)

    .. method:: pq[key]

    .. method:: pq[key] = value

    .. method:: del pq[key]

    .. method:: key in pq
    
    .. automethod:: get(key[, default])

    .. method:: pop([key[, default]])

        If ``key`` is in the pqdict, remove it and return its priority value,
        else return ``default``. If ``default`` is not provided and ``key`` is
        not in the pqdict, raise a ``KeyError``.

    .. automethod:: clear 
    
    .. automethod:: update([other]) 

    .. automethod:: setdefault(key[, default]) 

    .. automethod:: copy()

    Iterators and Views

    .. warning:: 
        For the following sequences, order is arbitrary.

    .. method:: iter(pq)

    .. automethod:: keys

    .. automethod:: values 

    .. automethod:: items

    .. note::
        In Python 2, the above methods return lists rather than views and ``pqdict`` includes additional iterator methods ``iterkeys()``, ``itervalues()`` and ``iteritems()``.

    |

    **Priority Queue API**

    .. automethod:: top
    
    .. method:: pop([key[, default]])

        If ``key`` is not provided, remove the top item and return its key, or
        raise ``KeyError`` if the pqdict is empty.

    .. automethod:: additem

    .. automethod:: updateitem

    .. automethod:: topitem

    .. automethod:: popitem

    .. automethod:: pushpopitem(key, value)

    .. automethod:: replace_key

    .. automethod:: swap_priority

    Heapsort Iterators

    .. note::
        Iteration is in descending order of priority.

    .. danger::
        Heapsort iterators are destructive: they are generators that pop items out of the heap, which amounts to performing a heapsort.

    .. automethod:: popkeys

    .. automethod:: popvalues 

    .. automethod:: popitems

    .. warning::
        The names of the heapsort iterators in v0.5 (iterkeys, itervalues, iteritems) were changed in v0.6 to be more transparent: These names are not provided at all in Python 3, and in Python 2 they are now part of the dictionary API.


Functions
---------
.. autofunction:: pqdict.nsmallest

.. autofunction:: pqdict.nlargest

