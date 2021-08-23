from networkx.algorithms.centrality.betweenness import betweenness_centrality
from networkx.algorithms.centrality.closeness import closeness_centrality
from networkx.algorithms.centrality.degree_alg import degree_centrality
import numpy as np
import networkx as nx
from src.modules.data import Data
from src.modules.network import Net
from src.modules.utils import distance_avg, hierarchical_clustering
from src.modules.ID3 import ID3
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('expand_frame_repr', False)


class _G():
    def __init__(self) -> None:
        pass

    @property
    def G(self):
        return self._G

    @G.setter
    def G(self, value):
        self._G = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def net(self):
        return self._net

    @net.setter
    def net(self, value):
        self._net = value


G = _G()


def data_overview(path="src/data/2019-world-copper-2063-trade.csv"):
    G.data = Data(path)
    G.net = Net(G.data)
    G.G = G.net.G
    return G.data.data


def check_data():
    allParticipants = G.data.getAllParticipants()
    allReporters = G.data.getAllReporters()
    allPartners = G.data.getAllPartners()

    print("上报进贸易记录的国家总数（不含重复）: ", allReporters.shape[0])
    print("上报进贸易记录的中的贸易对象国家总数（不含重复）: ", allPartners.shape[0])
    print("上报进贸易记录的国家，和记录中的贸易对象国家总数（不含重复）: ", allParticipants.shape[0])


def view_logs_by_china():
    chinaImportLog = G.data.getCountryLog(156, "Import")
    partnerNum1 = chinaImportLog.shape[0]

    print("中国上报的进口记录中，涉及出口国家的个数: ", partnerNum1)
    return chinaImportLog.head(partnerNum1)


def view_logs_about_china():
    exportToChinaLog = G.data.getCountryLog(156, "Export", "parter")
    partnerNum2 = exportToChinaLog.shape[0]

    print("全球上报了对中国有出口记录的国家", partnerNum2)
    return exportToChinaLog.head(partnerNum2)


def cluster_nodes(nodes, indictor, label_name, layers=6):
    """hierarchical cluster nodes by "indicoter", and label the cluster index

    Args:
        nodes: list
        indictor: string
        label_name: string
        layers: number

    Returns: (list, list)
    """

    # nodes = net.getSortedEntropies()
    nodes = sorted(nodes, key=lambda e: e[indictor], reverse=True)
    indictor_range = [item[indictor] for item in nodes]
    clusters = hierarchical_clustering(indictor_range, distance_avg, layers)

    cursor = 0
    label_value = 1
    for cluster in clusters:
        count = len(cluster)
        for i in range(cursor, cursor + count):
            nodes[i][label_name] = label_value

        cursor += count
        label_value += 1

    return (clusters, nodes)


# attribute_names = ["in_strength", "out_strength", "in_degree", "out_degree"]
attribute_names = ["IS", "OS", "DC", "BC", "CC"]


def set_attributes(nodes):
    degree_centralities = nx.degree_centrality(G.G)
    betweenness_centralities = nx.betweenness_centrality(G.G)
    closeness_centralities = nx.closeness_centrality(G.G)
    in_strengths = G.G.in_degree(weight="weight")
    out_strengths = G.G.out_degree(weight="weight")

    for node in nodes:
        node['IS'] = in_strengths[node['code']]
        node['OS'] = out_strengths[node['code']]
        node['DC'] = degree_centralities[node['code']]
        node['BC'] = betweenness_centralities[node['code']]
        node['CC'] = closeness_centralities[node['code']]

    attributes = {
        "IS": {"layer": 6},
        "OS": {"layer": 6},
        "BC": {"layer": 6},
        "DC": {"layer": 6},
        "CC": {"layer": 6},
    }

    return nodes, attributes


'''
def set_attributes(nodes):
    for node in nodes:
        node["in_strength"] = G.in_degree(node["code"], weight="weight")
        node["out_strength"] = G.out_degree(node["code"], weight="weight")
        node["in_degree"] = G.in_degree(node["code"])
        node["out_degree"] = G.out_degree(node["code"])

    attributes = {
        "in_degree": {"layer": 6},
        "out_degree": {"layer": 6},
        "in_strength": {"layer": 6},
        "out_strength": {"layer": 6}
    }

    return nodes, attributes
'''


def show_cluster_list(nodes, label_name):
    def join_value(value):
        return ",".join(value)

    label_group = pd.DataFrame(nodes)
    label_group[["code"]] = label_group[["code"]].astype('str')
    # res = label_group.groupby(label_name).apply(lambda x: ",".join(x["code"]))

    res = label_group.groupby(label_name).aggregate(
        {"code": join_value, "name": join_value})

    return res


def show_nodes_attribute(nodes):
    print(pd.DataFrame(nodes)[
        ['code', 'name'] +
        attribute_names + ['label']
    ].sort_values('label'))


def generate_decision_tree(data, attributes):
    dt = ID3()
    '''
    attribute_ranges = {
        "in_strength": [1, 2, 3, 4, 5, 6],
        "out_strength": [1, 2, 3, 4, 5, 6],
        "in_degree": [1, 2, 3, 4, 5, 6],
        "out_degree": [1, 2, 3, 4, 5, 6],
    }
    '''

    attribute_ranges = {}
    for name, value in attributes.items():
        attribute_ranges[name] = [i+1 for i in range(value['layer'])]

    return dt.generateTree(data, attribute_ranges)


def save_decision_tree(tree, to):
    ID3.saveDesicionTree(tree, to)


def show_dt_accuracy(data, tree):
    print("决策树的正确率：", ID3.checkPrecesion(data, tree) / len(data) * 100, "%")


def generate_list(tree):
    return ID3.generateList(tree)


def set_attribute_probability(nodes, attributes):
    for attr_values in attributes.values():
        attr_values['p'] = [len(item) / len(nodes)
                            for item in attr_values["cluster"]]

    return attributes


def show_attributes_distribution(attributes):
    dis = [{
        'Name': name,
        'Probability': [format(p, '.4f') for p in value['p']]
    } for name, value in attributes.items()]
    print(pd.DataFrame(dis))


def set_decision_probability(decision_list, attributes):
    for item in decision_list:
        p = 1
        for attr, value in item.items():
            if attr not in attributes.keys():
                continue
            p *= attributes[attr]['p'][int(value) - 1]

        item['p'] = p

    return decision_list


def show_decision_probability(decision_list):
    table = pd.DataFrame(decision_list)[attribute_names + ['label', 'p']]
    print(table)


def get_hierarchical_risk(decision_list):
    risk = [0 for _ in range(6)]

    for item in decision_list:
        risk[int(item['label']) - 1] += item['p']

    return risk


def decision_probability_bar(decision_list):
    ps = [[] for _ in range(6)]

    for item in decision_list:
        ps[int(item['label']) - 1].append(item['p'])

    plt.figure(figsize=(20, 20))

    width = 1
    group_gap = 5

    fig, ax = plt.subplots()

    last_index = 0
    ind = []
    xs = []

    for i in range(0, 6):
        group_len = len(ps[i])

        x = np.arange(group_len) + last_index + group_gap
        xs.append(x)

        last_index = x[-1]

        _ = ax.bar(x, ps[i], width)

    ind = [x for j in xs for x in j]

    x_labels = ['' for _ in range(len(ind))]

    former_index = 0
    for i, x in enumerate(xs):
        x_labels[former_index + int(len(x) / 2)] = i + 1
        former_index += len(x)

    ax.set_xticklabels(x_labels, fontsize=14)

    ax.set_ylabel('Probability', fontsize=14)
    ax.set_xticks(ind)

    plt.show()


def hierarchical_risk_bar(risks):
    plt.bar([i + 1 for i in range(6)], risks)

    plt.show()
