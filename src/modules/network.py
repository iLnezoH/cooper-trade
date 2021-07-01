import networkx as nx
import matplotlib.pyplot as plt


class Net():
    def __init__(self, data) -> None:
        self.data = data
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
                    G.add_edge(log._3, log._1, tradeValue=log._6)
            except KeyError:
                None

            try:
                exportPartnerLog = data.getCountryLog(
                    row.Code, "Export", "partner")
                for log in exportPartnerLog.itertuples():
                    G.add_node(log._3, label=log.Partner)
                    G.add_node(log._1, label=log.Reporter)
                    G.add_edge(log._1, log._3, tradeValue=log._6)
            except KeyError:
                None

        return G

    def draw(self):
        G = self.G

        nodesDict = dict(G.nodes(data=True))

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
        #nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=20)

        plt.show()
