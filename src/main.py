from matplotlib import RcParams
from networkx.algorithms import cluster
from networkx.algorithms.centrality.betweenness import betweenness_centrality
from networkx.algorithms.centrality.closeness import closeness_centrality
from networkx.algorithms.centrality.degree_alg import degree_centrality
from networkx.algorithms.coloring.greedy_coloring import strategy_largest_first
import numpy as np
import networkx as nx
from src.modules.data import Data
from src.modules.network import Net
from src.modules.utils import distance_avg, hierarchical_clustering
from src.modules.ID3 import ID3
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('expand_frame_repr', False)


class Report():
    attribute_names = ["IS", "OS", "DC", "BC", "CC"]

    def __init__(self, path, name) -> None:
        self.name = name
        self.data = Data(path)
        self.net = Net(self.data)
        self.G = self.net.G
        self.nodes = self.net.sortedNodes
        self.attributes = {
            "IS": {"layer": 6},
            "OS": {"layer": 6},
            "BC": {"layer": 6},
            "DC": {"layer": 6},
            "CC": {"layer": 6},
        }
        # self.decision_list = []
        # self.hierarchical_risk = []

    def data_overview(self, path="src/data/2019-world-copper-2063-trade.csv"):
        return self.data.data

    def check_data(self):
        allParticipants = self.data.getAllParticipants()
        allReporters = self.data.getAllReporters()
        allPartners = self.data.getAllPartners()

        print("上报进贸易记录的国家总数（不含重复）: ", allReporters.shape[0])
        print("上报进贸易记录的中的贸易对象国家总数（不含重复）: ", allPartners.shape[0])
        print("上报进贸易记录的国家，和记录中的贸易对象国家总数（不含重复）: ", allParticipants.shape[0])

    def view_logs_by_china(self):
        chinaImportLog = self.data.getCountryLog(156, "Import")
        partnerNum1 = chinaImportLog.shape[0]

        print("中国上报的进口记录中，涉及出口国家的个数: ", partnerNum1)
        return chinaImportLog.head(partnerNum1)

    def view_logs_about_china(self):
        exportToChinaLog = self.data.getCountryLog(156, "Export", "parter")
        partnerNum2 = exportToChinaLog.shape[0]

        print("全球上报了对中国有出口记录的国家", partnerNum2)
        return exportToChinaLog.head(partnerNum2)

    def set_attributes(self, attributes=None):
        degree_centralities = nx.degree_centrality(self.G)
        betweenness_centralities = nx.betweenness_centrality(self.G)
        closeness_centralities = nx.closeness_centrality(self.G)
        in_strengths = self.G.in_degree(weight="weight")
        out_strengths = self.G.out_degree(weight="weight")

        for node in self.nodes:
            node['IS'] = in_strengths[node['code']]
            node['OS'] = out_strengths[node['code']]
            node['DC'] = degree_centralities[node['code']]
            node['BC'] = betweenness_centralities[node['code']]
            node['CC'] = closeness_centralities[node['code']]

        if attributes is None:
            self.attributes = {
                "IS": {"layer": 6},
                "OS": {"layer": 6},
                "BC": {"layer": 6},
                "DC": {"layer": 6},
                "CC": {"layer": 6},
            }
        else:
            self.attributes = attributes

    def cluster_nodes(self):
        Report.cluster_nodes_by(self.nodes, 'E', 'label', 6)
        self.set_attributes()

        for attr, values in self.attributes.items():
            cluster, self.nodes = Report.cluster_nodes_by(
                self.nodes, attr, attr, values["layer"])

            values["cluster"] = cluster

    def show_nodes_attribute(self):
        return pd.DataFrame(self.nodes)[
            ['code', 'name'] +
            Report.attribute_names + ['label']
        ].sort_values('label').reset_index(drop=True)

    @staticmethod
    def cluster_nodes_by(nodes, indictor, label_name, layers=6):
        """hierarchical cluster nodes by "indicoter", and label the cluster index

        Args:
            nodes: list
            indictor: string
            label_name: string
            layers: number

        Returns: (list, list)
        """

        nodes = sorted(nodes, key=lambda e: e[indictor], reverse=True)
        indictor_range = [item[indictor] for item in nodes]
        clusters = hierarchical_clustering(
            indictor_range, distance_avg, layers)

        cursor = 0
        label_value = 1
        for cluster in clusters:
            count = len(cluster)
            for i in range(cursor, cursor + count):
                nodes[i][label_name] = label_value

            cursor += count
            label_value += 1

        return (clusters, nodes)

    @property
    def decision_tree(self):
        dt = ID3()
        attribute_ranges = {}
        for name, value in self.attributes.items():
            attribute_ranges[name] = [i+1 for i in range(value['layer'])]

        return dt.generateTree(self.nodes, attribute_ranges)

    @property
    def decision_attribute_distribute(self):
        distribute = {}
        for attr in self.attribute_names:
            distribute[attr] = 0

        for attr in self.attribute_names:
            for path in self.decision_list:
                try:
                    if path[attr]:
                        None
                    distribute[attr] += 1 / len(self.decision_list)
                except KeyError:
                    None
        return distribute

    '''
    def generate_decision_tree(self):
        dt = ID3()
        attribute_ranges = {}
        for name, value in self.attributes.items():
            attribute_ranges[name] = [i+1 for i in range(value['layer'])]

        self.decision_tree = dt.generateTree(self.nodes, attribute_ranges)
    '''

    def save_decision_tree(self, to):
        ID3.saveDesicionTree(self.decision_tree, to)

    def show_dt_accuracy(self):
        print("决策树的正确率：", ID3.checkPrecesion(
            self.nodes, self.decision_tree) / len(self.nodes) * 100, "%")

    @property
    def decision_list(self):
        _list = ID3.generateList(self.decision_tree)
        for item in _list:
            p = 1
            for attr, value in item.items():
                if attr not in self.attributes.keys():
                    continue
                p *= self.attributes[attr]['p'][int(value) - 1]

            item['p'] = p

        return _list

    # @decision_list.setter
    '''
    def generate_decision_list(self):
        self.decision_list = ID3.generateList(self.decision_tree)
    '''

    def set_attribute_probability(self):
        for attr_values in self.attributes.values():
            attr_values['p'] = [len(item) / len(self.nodes)
                                for item in attr_values["cluster"]]

    def show_attributes_distribution(self):
        dis = [{
            'Name': name,
            'Probability': [format(p, '.4f') for p in value['p']]
        } for name, value in self.attributes.items()]
        print(pd.DataFrame(dis))

    def show_decision_probability(self):
        table = pd.DataFrame(self.decision_list)[
            Report.attribute_names + ['label', 'p']]
        print(table)

    @property
    def hierarchical_risk(self):
        risk = [0 for _ in range(6)]

        for item in self.decision_list:
            risk[int(item['label']) - 1] += item['p']

        return risk

    def decision_probability_bar(self):

        ps = [[] for _ in range(6)]

        for item in self.decision_list:
            ps[int(item['label']) - 1].append(item['p'])

        fig, ax = plt.subplots(figsize=(20, 20))

        width = 1
        group_gap = 5

        last_index = 0
        ind = []
        xs = []

        for i in range(0, 6):
            _ps_i = ps[i] or [0]

            group_len = len(_ps_i)

            offset = last_index + group_gap

            x = np.arange(group_len) + offset
            xs.append(x)

            ax.bar(x, _ps_i, width)

            # label max probability in the cluster
            max_p = max(_ps_i)
            max_p_x = _ps_i.index(max_p) + offset
            ax.text(max_p_x, max_p + 0.001, round(max_p, 4), ha="center")

            # label num of paths of the cluster
            ps_i_num = len(_ps_i)
            ax.text((ps_i_num - 1) / 2 + offset, max_p +
                    0.006, ps_i_num, ha="center", fontsize=20)

            last_index = x[-1]

        ind = [x for j in xs for x in j]

        x_labels = ['' for _ in range(len(ind))]

        former_index = 0
        for i, x in enumerate(xs):
            x_labels[former_index + int(len(x) / 2)] = i + 1
            former_index += len(x)

        ax.set_ylabel(r'$P_{Path_l}$', fontsize=24)
        ax.set_xlabel(r'j', fontsize=24)
        # ax.set_xticks(ind, x_labels)
        ax.set_xticks(ind)
        ax.set_xticklabels(x_labels)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.show()

    def hierarchical_risk_bar(self):
        plt.bar([i + 1 for i in range(6)], self.hierarchical_risk)

        plt.show()

    def draw_entropy_plot(self, rank=None,  ylabel="adjacency information entropy"):
        entropies = self.net.sortedNodes
        x = [i for i in range(1, len(entropies) + 1)]
        y = [item['E'] for item in entropies]

        if rank is None:
            plt.plot(x, y, '-', label=self.name)
        else:
            plt.plot(x[0: rank], y[0: rank], '-', label=self.name)
        plt.ylabel(ylabel)


def show_cluster_list(reports, label_name="label"):
    def join_value(value):
        length = len(value)
        if length < 10:
            return ",".join(value)
        else:
            return ",".join(value[0:4]) + ",等" + str(length) + "项"

    res = []
    for _nodes in [r.nodes for r in reports]:

        label_group = pd.DataFrame(_nodes)
        label_group[["code"]] = label_group[["code"]].astype('str')
        # res = label_group.groupby(label_name).apply(lambda x: ",".join(x["code"]))

        res.append(label_group.groupby(label_name).aggregate(
            {"code": join_value}))

    return pd.concat(res, axis=1)


def write_to_excel(dataFrame, path):
    writer = pd.ExcelWriter(path)
    dataFrame.to_excel(writer, float_format='%.5f')
    writer.save()


def get_decision_attribute_distribute(reports):

    attribute_distribute = {}

    for report in reports:
        attribute_distribute[report.name] = report.decision_attribute_distribute

    return pd.DataFrame(attribute_distribute)


def show_hierarchical_risk_bar(reports):
    plt.figure(figsize=(13, 10))
    fig, axes = plt.subplots(figsize=(12, 10))

    years = len(reports)
    offset = -(years - 1) / 2

    x = np.arange(len(reports[0].hierarchical_risk)) + 1
    width = 0.08
    for i, report in enumerate(reports):
        axes.bar(x + (offset + i) * width, report.hierarchical_risk,
                 width=width, label=report.name)

    axes.legend()
    axes.set_xlabel(r'$j$', fontsize=20)
    axes.set_ylabel(r'$P_j$', fontsize=20)
    axes.spines['right'].set_visible(False)
    axes.spines['top'].set_visible(False)

    plt.show()
