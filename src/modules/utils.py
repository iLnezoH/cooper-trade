import math


def getEntropy(ps):
    for p in ps:
        if(p < 0 or p > 1):
            raise ValueError("p must in (0,1)")
    pLogP = [-p * math.log(p, 2) for p in ps if p > 0]
    return sum(pLogP)
