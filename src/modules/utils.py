import math


def getEntropy(ps):
    for p in ps:
        if(p < 0 or p > 1):
            raise ValueError("p must in (0,1)")
    pLogP = [-p * math.log(p, 2) for p in ps if p > 0]
    return sum(pLogP)


def getStrength(G, node, l=0.75):
    in_edges = G.in_edges(node, data="weight")
    out_edges = G.out_edges(node, data="weight")

    in_strength = sum([data[2] for data in in_edges])
    out_strength = sum([data[2] for data in out_edges])

    return l * in_strength + (1 - l) * out_strength


def getAdjacencyDegree(G, node, theta=0.75, l=0.75):
    successors = G.successors(node)
    predecessors = G.predecessors(node)

    in_degree = sum([getStrength(G, node, l) for node in predecessors])
    out_degree = sum([getStrength(G, node, l) for node in successors])

    return theta * in_degree + (1 - theta) * out_degree


def getSelectionProbability(G, i, j, theta=0.75, l=0.75):
    return getStrength(G, i, l) / getAdjacencyDegree(G, j, theta, l)


def getAdjacencyEntropy(G, i, theta=0.75, l=0.75):
    successors = G.successors(i)
    predecessors = G.predecessors(i)

    neighbors = set((*successors, *predecessors))

    E = 0

    for neighbor in neighbors:
        p = getSelectionProbability(G, i, neighbor, theta, l)
        E += abs(p * math.log(p, 2))

    return E
