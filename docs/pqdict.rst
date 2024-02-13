API Reference
=============

.. toctree::
   :maxdepth: 2

.. currentmodule:: pqdict


pqdict class
------------
.. autoclass:: pqdict
    :no-members:

    .. automethod:: __init__

    .. automethod:: minpq

    .. automethod:: maxpq
    
    .. automethod:: fromkeys

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

        Hybrid pop method.

        With ``key``, perform a dictionary pop:
        
        * If ``key`` is in the pqdict, remove the item and return its
          **value**.
        * If ``key`` is not in the pqdict, return ``default`` if provided,
          otherwise raise a ``KeyError``.

    .. automethod:: clear 
    
    .. automethod:: update([other]) 

    .. automethod:: setdefault(key[, default]) 

    .. automethod:: copy()

    Iterators and Views

    .. warning:: 
        For the sequences returned by the following methods, the **iteration order is arbitrary**.

        See further below for sorted iterators :meth:`popkeys`, :meth:`popvalues`, and :meth:`popitems`.

    .. method:: iter(pq)

    .. automethod:: keys

    .. automethod:: values 

    .. automethod:: items

    |

    **Priority Queue API**

    .. automethod:: top

    .. automethod:: topvalue

    .. automethod:: topitem
    
    .. method:: pop(*, [default])

        Hybrid pop method.

        Without ``key``, perform a priority queue pop:

        * Remove the top item and return its **key**.
        * If the pqdict is empty, return ``default`` if provided, otherwise
          raise ``Empty``.

    .. automethod:: popvalue
    
    .. automethod:: popitem

    .. automethod:: additem

    .. automethod:: updateitem

    .. automethod:: pushpopitem(key, value)

    .. automethod:: replace_key

    .. automethod:: swap_priority

    .. automethod:: heapify([key])

    Sorted Iterators

    .. note::
        Iteration is in descending order of priority.

    .. warning::
        Sorted iterators are destructive: they are generators that pop items out of the heap, which amounts to performing a heapsort.

    .. automethod:: popkeys

    .. automethod:: popvalues 

    .. automethod:: popitems


Functions
---------
.. autofunction:: pqdict.nsmallest

.. autofunction:: pqdict.nlargest

