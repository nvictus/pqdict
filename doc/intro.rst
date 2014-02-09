.. include:: ../README.rst

-----

.. warning::
	WARNING: Any dictionary key's assigned priority key can be changed to a different one (i.e., the mapping is mutable), but for much the same reason that dictionary keys in Python must be immutable objects, priority keys should also be **immutable** objects (e.g., numbers, strings, tuples, datetime). However, this is not enforced: if you do happen to use mutable objects as priority keys, any modification to those objects could break your priority queue!

