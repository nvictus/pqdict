Priority Queue Dictionary (pqdict)
=========================

An indexed priority queue implementation written in Python. The `PQDict` class provides the `MutableMapping` protocol and its instances operate like regular Python dictionaries with a couple extra methods. Think of a Priority Queue Dictionary as a mapping of "dictionary keys" to "priority keys".

## What is an "indexed" priority queue?
A [priority queue](http://en.wikipedia.org/wiki/Priority_queue) is an abstract data structure that allows you to serve elements in a prioritized fashion. You can insert elements with priorities, and remove or peek at the top priority element. Unlike a standard priority queue, an _indexed_ priority queue additionally allows you to alter the priority of any element in the queue. With the right implementation, each of these operations can be done quite efficiently.

## How does it work?
The priority queue is implemented as a binary heap (using a python list), which supports:  

- O(1) access to the top priority element

- O(log n) removal of the top priority element

- O(log n) insertion of a new element

In addition, an internal dictionary or "index" maps elements to their position in the heap. This index is synchronized with the heap as the heap is manipulated. As a result, `PQDict` also supports:     

- O(1) lookup of an arbitrary element's priority key

- O(log n) removal of an arbitrary element 

- O(log n) updating of an arbitrary element's priority key

## Why would I want something like that?
Indexed priority queues can be very useful as schedulers for applications like [simulations](http://pubs.acs.org/doi/abs/10.1021/jp993732q). They can also be used in efficient implementations of Dijkstra's shortest-path algorithm. Basically, whenever we not only want to be able to quickly find the minimum or maximum element, but we also need to be able to dynamically find and modify the priorities of existing elements in the queue efficiently.

## Examples
By default, `PQDict` uses a min-heap, meaning **smaller** priority keys have **higher** priority. Use `PQDict.maxpq()` to create a max-heap priority queue.

```python
from pqdict import PQDict

# same input signature as dict()
pq = PQDict(a=3, b=5, c=8)
pq = PQDict(zip(['a','b','c'], [3, 5, 8]))
pq = PQDict({'a':3, 'b':5, 'c':8})          

print pq.items()     # [('a',3), ('b',5), ('c',8)]



# add/update items this way...
pq.additem('d', 15)
pq.updateitem('c', 1)

# ...or this way
pq['d'] = 6.5
pq['e'] = 2
pq['f'] = -5

print pq.keys()     # ['f', 'c', 'a', 'd', 'e', 'b']



# get an element's priority
pkey = pq['f']
print pkey          # -5
print 'f' in pq     # True

# remove an element and get its priority key
pkey = pq.pop('f')
print pkey          # -5
print 'f' in pq     # False

pkey = pq.get('f', None)
print pkey          # None

# or just delete an element
del pq['e']
print pq.keys()     # ['c', 'b', 'a', 'd']



# peek at the top priority item
print pq.peek()     # ('c', 1)



# let's do a manual heapsort
print pq.popitem()  # ('c', 1)
print pq.popitem()  # ('a', 3)
print pq.popitem()  # ('b', 5)
print pq.popitem()  # ('d', 6.5)



# and we're empty!
pq.popitem()        # KeyError
```

Regular iterators have no prescribed order and are non-destructive:
```python
queue = PQDict({'Alice':1, 'Bob':2})
for customer in queue:
	serve(customer) #Bob may be served before Alice!

pq.keys()
pq.values()
pq.items()
```

Destructive iteration methods return generators that use heapsort:
```python
for customer in queue.iterkeys():
	serve(customer) #Customers satisfaction guaranteed
# queue is now empty

pq.iterkeys()
pq.itervalues()
pq.iteritems()
```

There is also a convenience method to sort a dictionary-like object by value using a PQDict. It is non-destructive:
```python
from pqdict import heapsort

billionaires = {'Bill Gates': 72.7, 'Warren Buffett': 60.0, ...}
for person, wealth in heapsort(billionaires, maxheap=True):
	print person + 'has $' + wealth + 'B'
```
## License
This module was written by Nezar Abdennur and is released under the MIT license. It makes use of some code that was adapted from the Python implementation of the `heapq` module, which was written by Kevin O'Connor and augmented by Tim Peters and Raymond Hettinger.
