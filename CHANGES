Release Notes
=============


1.1.0 (2020-08-21)
++++++++++++++++++

* API changes:
	- ``nlargest`` and ``nsmallest`` now support an optional ``key`` parameter (#10). By `Eugene Prilepin <https://github.com/espdev>`_.


1.0.1 (2020-07-12)
++++++++++++++++++

* Maintenance:
	- Dropped 3.3 support.
	- Future-proofed for upcoming collections import breakage (#6). By `R. Bernstein <https://github.com/rocky>`_.
	- Upgraded test suite from nose to pytest (#7). By `R. Bernstein <https://github.com/rocky>`_.


1.0.0 (2015-09-02)
++++++++++++++++++

* Stable release.

* Supporting 2.7+, 3.3+ and pypy. Dropped 3.2 support.


0.6 (2015-08-31)
++++++++++++++++

* Conceptual changes:
	- Clearer terminology in API and documentation (e.g., value vs. priority 
	  key).
	- Functional philosophy: pqdict accepts optional priority key function and 
	  precedence function.
* API changes:
	- PQDict name is deprecated.
	- Several backwards-incompatible changes to fit the new conceptual model.
	- Heapsort iterators (iterkeys, itervalues, iteritems) were renamed 
	  (popkeys, popvalues, popitems). In Python 2, the old names persist as 
	  regular iterators.
	- Dropped module functions except for nlargest and nsmallest.
* Docs:
	- Revised and updated
	- Switch to RTD theme


0.5 (2014-02-09)
++++++++++++++++

* API changes:
	- PQDict.pq_type property: 'min', 'max' or 'custom'
	- fromkeys keyword 'sort_by' is replaced with 'rank_by'
* Bug fixes:
	- turns out PQDict.create and sort_by_value were broken! (oops!)
	- consume: the collector was comparing the wrong pkeys
* Improved test coverage:
	- improved coverage of unit tests
	- using travis-ci


0.4 (2013-12-08)
++++++++++++++++

* API changes:
	- renamed peek() to top()
	- semantics of top, pop, vs. topitem, popitem, *item, now hopefully more 
	  consistent
	- prioritykeys() and iterprioritykeys() are aliases for values() and 
	  itervalues()
	- new methods: pushpopitem, swap_priority, replace_key
* New functions:
	- nsmallest, nlargest
	- consume
* Added Sphinx documentation


0.3 (2013-07-23)
++++++++++++++++

* Bug fixes:
	- off-by one error caused the queue to not reheapify properly in a special 
	  case


0.2 (2013-07-18)
++++++++++++++++

* Bug fixes:
	- Fixed error in __all__ list


0.1 (2013-07-17)
++++++++++++++++

* First release.
