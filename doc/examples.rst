Examples
========

Here's a simple example of implementing Dijkstra's algorithm using a ``PQDict``.

.. raw:: html

	<script src="https://gist.github.com/nvictus/7854213.js"></script>


-----

:py:meth:`pqdict.nsmallest` and :py:meth:`pqdict.nlargest` basically work like the functions of the name in ``heapq`` but act on dictionaries and dict-like objects instead, sorting by value.

.. code:: python 

    from pqdict import nlargest

    billionaires = {'Bill Gates': 72.7, 'Warren Buffett': 60.0, ...}
    top10_richest = nlargest(10, billionaires)