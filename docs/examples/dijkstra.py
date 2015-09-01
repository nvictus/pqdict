import pqdict

def dijkstra(graph, source, target=None):
    """
    Computes the shortests paths from a source vertex to every other vertex in
    a graph

    """
    # The entire main loop is O( (m+n) log n ), where n is the number of
    # vertices and m is the number of edges. If the graph is connected
    # (i.e. the graph is in one piece), m normally dominates over n, making the
    # algorithm O(m log n) overall.

    dist = {}   
    pred = {}

    # Store distance scores in a priority queue dictionary
    pq = pqdict.PQDict()
    for node in graph:
        if node == source:
            pq[node] = 0
        else:
            pq[node] = float('inf')

    # Remove the head node of the "frontier" edge from pqdict: O(log n).
    for node, min_dist in pq.iteritems():
        # Each node in the graph gets processed just once.
        # Overall this is O(n log n).
        dist[node] = min_dist
        if node == target:
            break

        # Updating the score of any edge's node is O(log n) using pqdict.
        # There is _at most_ one score update for each _edge_ in the graph.
        # Overall this is O(m log n).
        for neighbor in graph[node]:
            if neighbor in pq:
                new_score = dist[node] + graph[node][neighbor]
                if new_score < pq[neighbor]:
                    pq[neighbor] = new_score
                    pred[neighbor] = node

    return dist, pred

def shortest_path(graph, source, target):
    dist, pred = dijkstra(graph, source, target)
    end = target
    path = [end]
    while end != source:
        end = pred[end]
        path.append(end)        
    path.reverse()
    return path

if __name__=='__main__':
    # A simple edge-labeled graph using a dict of dicts
    graph = {'a': {'b':14, 'c':9, 'd':7},
             'b': {'a':14, 'c':2, 'e':9},
             'c': {'a':9, 'b':2, 'd':10, 'f':11},
             'd': {'a':7, 'c':10, 'f':15},
             'e': {'b':9, 'f':6},
             'f': {'c':11, 'd':15, 'e':6}}

    dist, path = dijkstra(graph, source='a')
    print dist
    print path
    print shortest_path(graph, 'a', 'e')
