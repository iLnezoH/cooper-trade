import networkx as nx
import matplotlib.pyplot as plt
import collections

from src.modules.utils import getEntropy


class Net():
    def __init__(self, data) -> None:
        self.data = data
        self.initialEdges = []
        self.G = self._generateNet(data)

    def _generateNet(self, data):

        G = nx.DiGraph()
        allParticipants = data.getAllParticipants()

        for row in allParticipants.itertuples():
            try:
                selfImportLog = data.getCountryLog(row.Code, "Import", "self")
                for log in selfImportLog.itertuples():
                    G.add_node(log._3, label=log.Partner)
                    G.add_node(log._1, label=log.Reporter)
                    if (self._repeatEdgeCheck(log._3, log._1)):
                        continue
                    self.initialEdges.append([log._3, log._1])
                    # G.add_edge(log._3, log._1, tradeValue=log._6)
                    G.add_edge(log._3, log._1)
            except KeyError:
                None

            try:
                exportPartnerLog = data.getCountryLog(
                    row.Code, "Export", "partner")
                for log in exportPartnerLog.itertuples():
                    G.add_node(log._3, label=log.Partner)
                    G.add_node(log._1, label=log.Reporter)
                    if (self._repeatEdgeCheck(log._1, log._3)):
                        continue
                    self.initialEdges.append([log._1, log._3])
                    # G.add_edge(log._1, log._3, tradeValue=log._6)
                    G.add_edge(log._1, log._3)
            except KeyError:
                None

        return G

    def _repeatEdgeCheck(self, u, v):
        for (_u, _v) in self.initialEdges:
            if _u == u and _v == v:
                return True
        return False

    def getEntropy(self):

        degreeCount = self.getDegreeCount()

        distribute = list(degreeCount.values())
        amount = sum(distribute)

        E0 = getEntropy([x/amount for x in distribute])

        return E0

    def getDegreeCount(self):
        degree_sequence = sorted(
            [d for n, d in self.G.degree()], reverse=True)  # degree sequence

        return collections.Counter(degree_sequence)

    def degreeDisBar(self, width=0.8, color="b"):
        G = self.G

        degreeCount = self.getDegreeCount()

        deg, cnt = zip(*degreeCount.items())

        plt.bar(deg, cnt, width=width, color=color)
        plt.show()

    def draw(self):
        G = self.G

        nodeStrength = list(G.degree(weight="tradeValue"))

        sortedNodeStrenght = sorted(nodeStrength, key=lambda item: item[1])

        minStrength = sortedNodeStrenght[0][1]
        maxStrength = sortedNodeStrenght[-1][1]

        node_sizes = [
            300 + (item[1] - minStrength)
            / (maxStrength - minStrength)
            * 6000
            for item in nodeStrength
        ]

        plt.figure(3, figsize=(30, 30))
        pos = nx.random_layout(G)
        # pos = nx.spiral_layout(G)
        nx.draw(G, pos, with_labels=False, node_size=node_sizes)

        node_labels = nx.get_node_attributes(G, 'label')
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=20)

        # edge_labels = nx.get_edge_attributes(G, 'tradeValue')
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=20)

        plt.show()
