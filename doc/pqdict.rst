API Reference
=============

``PQDict`` class
----------------
.. autoclass:: pqdict.PQDict

    .. automethod:: pqdict.PQDict.minpq

    .. automethod:: pqdict.PQDict.maxpq

    .. automethod:: pqdict.PQDict.create

    .. automethod:: pqdict.PQDict.fromkeys

Dictionary Methods
^^^^^^^^^^^^^^^^^^
    These should work as expected. See :py:class:`dict` for more details.

    .. method:: len(pq)

    .. method:: pq[dkey]

    .. method:: pq[dkey] = pkey

    .. method:: del pq[dkey]

    .. method:: dkey in pq

    .. method:: PQDict.keys

    .. method:: PQDict.values 

    .. method:: PQDict.items
    
    .. method:: PQDict.get(dkey[, default]) 

    .. method:: PQDict.clear 
    
    .. method:: PQDict.update([other]) 

    .. method:: PQDict.setdefault(dkey[, default]) 

    .. automethod:: pqdict.PQDict.copy


Priority Queue Methods
^^^^^^^^^^^^^^^^^^^^^^

    .. method:: PQDict.prioritykeys

        Equivalent to :py:meth:`~pqdict.PQDict.values`

    .. automethod:: pqdict.PQDict.top
    
    .. automethod:: pqdict.PQDict.pop([dkey[, default]])

    .. automethod:: pqdict.PQDict.additem

    .. automethod:: pqdict.PQDict.updateitem

    .. automethod:: pqdict.PQDict.topitem

    .. automethod:: pqdict.PQDict.popitem

    .. automethod:: pqdict.PQDict.pushpopitem

    .. automethod:: pqdict.PQDict.replace_key

    .. automethod:: pqdict.PQDict.swap_priority


Iteration
^^^^^^^^^
    .. method:: iter(pq)

        Returns an iterator over the dictionary keys of the PQD. **The order of iteration is arbitrary!**

    .. automethod:: pqdict.PQDict.iterkeys

    .. automethod:: pqdict.PQDict.itervalues 

    .. automethod:: pqdict.PQDict.iteritems

    .. method:: PQDict.iterprioritykeys

        Equivalent to :py:meth:`~pqdict.PQDict.itervalues`


Functions
---------
.. autofunction:: pqdict.sort_by_value

.. autofunction:: pqdict.nsmallest

.. autofunction:: pqdict.nlargest

.. autofunction:: pqdict.consume
