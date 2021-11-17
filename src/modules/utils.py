import math

from networkx.classes.function import neighbors


def get_a_list(value):
    """ Always return a lsit: if 'value' is a list, just return itselft, else return [value] 

    Args:
        value: any,

    Returns: list
    """
    return value if isinstance(value, list) else [value]


def getEntropy(ps):
    """ Calculate Information Entropy

    Args:
        ps: [probability]

    Returns: number
        the information entropy

    Raises:
        ValueError: An error occured when some p not in (0, 1)
    """
    for p in ps:
        if(p < 0 or p > 1):
            raise ValueError("p must in (0,1)")
    pLogP = [-p * math.log(p, 2) for p in ps if p > 0]
    return sum(pLogP)


def getStrength(G, node, l=None):
    """ get strength of node in net directed and weighted G

    result = l * in_strength + (1 - l) * out_strength

    Args:
        G: network.DiGraph
        node: any, 
        l: number, weight fo in_strength and out_strength

    Returns: number, result
    """

    in_edges = G.in_edges(node, data="weight")
    out_edges = G.out_edges(node, data="weight")

    in_strength = sum([data[2] for data in in_edges])
    out_strength = sum([data[2] for data in out_edges])

    if l is None:
        return in_strength + out_strength

    return l * in_strength + (1 - l) * out_strength


def getAdjacencyDegree(G, node, theta=None, l=None):
    successors = G.successors(node)
    predecessors = G.predecessors(node)

    if theta is None:
        neighbors = set((*successors, *predecessors))
        return sum([getStrength(G, node, None) for node in neighbors])

    in_degree = sum([getStrength(G, node, l) for node in predecessors])
    out_degree = sum([getStrength(G, node, l) for node in successors])

    return theta * in_degree + (1 - theta) * out_degree


def getSelectionProbability(G, i, j, theta=None, l=None):
    return getStrength(G, i, l) / getAdjacencyDegree(G, j, theta, l)


def getAdjacencyEntropy(G, i, theta=None, l=None):
    successors = G.successors(i)
    predecessors = G.predecessors(i)

    neighbors = set((*successors, *predecessors))

    E = 0

    for neighbor in neighbors:
        p = getSelectionProbability(G, i, neighbor, theta, l)
        E += abs(p * math.log(p, 2))

    return E


def distance(cluster1, cluster2):
    """ Calculate distance of tow list basing on Euclidean distance

    Args:
        cluster1: list
        cluster2: list

    Returns: (number, number, number),
        return (average, max, min) distance of two list
    """

    dist_total = 0
    dist_max = 0
    dist_min = float("inf")
    len1 = len(cluster1)
    len2 = len(cluster2)
    for i in range(len1):
        for j in range(len2):
            current_dist = math.dist(get_a_list(
                cluster1[i]), get_a_list(cluster2[j]))
            dist_total += current_dist
            if current_dist < dist_min:
                dist_min = current_dist
            if current_dist > dist_max:
                dist_max = current_dist
    return (dist_total / (len1 * len2), dist_max, dist_min)


def distance_avg(cluster1, cluster2):
    return distance(cluster1, cluster2)[0]


def distance_min(cluster1, cluster2):
    return distance(cluster1, cluster2)[1]


def distance_max(cluster1, cluster2):
    return distance(cluster1, cluster2)[2]


def hierarchical_clustering(samples, dist_fn, k, _recursion_call=False):
    """ hierarchical clustering numerical samples
        ! this function will change 'samples' directly. Be sure backup the 'samples' if you want remain the original data

    Args:
        samples: [number]
        dist_fn: function, indicator to measure ditance of tow cluster
        k: clusters' count of the result
        _recursion_call: bool, needen't set when call the fn externally

    Returns: [list]
        'k' divided cluster from samples

    """
    if (not _recursion_call):
        samples = [[item] for item in samples]

    if k >= len(samples):
        return samples

    min_dist = float('inf')
    min_dist_index = [0, 0]

    for i in range(len(samples)):
        for j in range(len(samples)):
            if i == j:
                continue

            current_dist = dist_fn(samples[i], samples[j])
            if current_dist < min_dist:
                min_dist = current_dist
                min_dist_index = [i, j]

    min_dist_index.sort()

    to_merge = samples.pop(min_dist_index[1])
    samples[min_dist_index[0]].extend(to_merge)

    return hierarchical_clustering(samples, dist_fn, k, True)


def classifyByKey(collection, key):
    """classify "collection" by "key"

    Args:
        collection: list<dict>, to be classified
        key: string, the key of dict which devide "collection" by

    Returns: dict<key: list<dict>>
        a dict classfied by "key"
    """

    traveledKeys = []
    res = {}
    for item in collection:
        value = item[key]
        if (item[key] not in traveledKeys):
            res[value] = []
            traveledKeys.append(value)
        res[value].append(item)
    return res
