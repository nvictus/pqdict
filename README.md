Priority Queue Dictionary (pqdict)
=========================

An indexed priority queue data implementation written in python. The `PQDict` class provides the `MutableMapping` protocol and operates like a python dictionary with a couple extra methods. Think of it as a mapping of "dictionary keys" to "priority keys".

## What is an _indexed_ priority queue?
A priority queue is an abstract data structure that performs a basic service: serve the element of highest priority first. You can insert elements with priorities, and remove or peek at the top priority element. An indexed priority queue additionally allows you to alter the priority of a particular element. With the right implementation, these operations can be done efficiently.

## How does it work?
The priority queue is implemented as a binary heap (using a python list), which supports:  

- O(1) access to the top priority item

- O(log n) deletion of the top priority item

- O(log n) insertion of a new item

In addition, an internal dictionary or "index" maps items to their position in the heap. This index is synchronized with the heap as it is manipulated. As a result, `PQDict` also supports:     

- O(1) lookup of an arbitrary item's priority key

- O(log n) deletion of an arbitrary item     

- O(log n) updating of an arbitrary item's priority key

## Why would I want that?
Indexed priority queues can be very useful as schedulers for applications like simulation, or in efficient implementations of Dijkstra's shortest-path algorithm. Basically, when not only is efficiently extracting the minimum or maximum important, but also the ability to efficiently modify the priority of an arbitrary element in the queue.

## Examples
By default, `PQDict` uses a min-heap, meaning **smaller** priority keys have "higher" priority. Use `PQDict.maxpq()` to create a max-heap priority queue.

```python
from pqdict import PQDict

# accepts same input signatures as dict()
#pq = PQDict(a=3, b=5, c=8)
#pq = PQDict( [('a',3), ('b',5), ('c',8)] )
pq = PQDict({'a':3, 'b':5, 'c':8})          

print pq           #PQDict({'a': 3, 'c': 8, 'b': 5})
```

```python
# add/update items this way...
pq.additem('d', 15)
pq.updateitem('c', 1)

# ...or this way
pq['d'] = 6.5
pq['e'] = 2
pq['f'] = -5

print pq           #PQDict({'f': -5, 'c': 1, 'a': 3, 'd': 6.5, 'e': 2, 'b': 5})
```


```python
# get an element's priority
pkey = pq['f']
print pkey         #-5
print 'f' in pq    #True

# pop and get element's priority key
pkey = pq.pop('f')
print pkey         #-5
print 'f' in pq    #False

pkey = pq.get('f', None)
print pkey         #None

# or just delete an element
del pq['e']
print pq           #PQDict({'c': 1, 'b': 5, 'a': 3, 'd': 6.5})
```

```python
# peek at the top priority item
print pq.peek()    #('c', 1)
```

```python
# do a heapsort
print pq.popitem() #('c', 1)
print pq.popitem() #('a', 3)
print pq.popitem() #('b', 5)
print pq.popitem() #('d', 6.5)
```


```python
# we're empty!
pq.popitem()       #KeyError
```
