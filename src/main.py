from networkx.algorithms.dag import root_to_leaf_paths
from src.modules.data import Data
from src.modules.network import Net
from src.modules.utils import distance_avg, hierarchical_clustering
from src.modules.ID3 import ID3
import pandas as pd


data = Data("src/data/2019-world-copper-2063-trade.csv")

net = Net(data)
G = net.G


def data_overview():
    return data.data


def check_data():
    allParticipants = data.getAllParticipants()
    allReporters = data.getAllReporters()
    allPartners = data.getAllPartners()

    print("上报进贸易记录的国家总数（不含重复）: ", allReporters.shape[0])
    print("上报进贸易记录的中的贸易对象国家总数（不含重复）: ", allPartners.shape[0])
    print("上报进贸易记录的国家，和记录中的贸易对象国家总数（不含重复）: ", allParticipants.shape[0])


def view_logs_by_china():
    chinaImportLog = data.getCountryLog(156, "Import")
    partnerNum1 = chinaImportLog.shape[0]

    print("中国上报的进口记录中，涉及出口国家的个数: ", partnerNum1)
    return chinaImportLog.head(partnerNum1)


def view_logs_about_china():
    exportToChinaLog = data.getCountryLog(156, "Export", "parter")
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
            nodes[i][label_name] = int(label_value)

        cursor += count
        label_value += 1

    return (clusters, nodes)


attribute_names = ["in_strength", "out_strength", "in_degree", "out_degree"]


def set_attributes(nodes):
    for node in nodes:
        node["in_strength"] = G.in_degree(node["code"], weight="weight")
        node["out_strength"] = G.out_degree(node["code"], weight="weight")
        node["in_degree"] = G.in_degree(node["code"])
        node["out_degree"] = G.out_degree(node["code"])

    return nodes


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
    pd.DataFrame(nodes).head(len(nodes))


def generate_Decision_Tree(data):
    dt = ID3()
    attribute_ranges = {
        "in_strength": [1, 2, 3, 4, 5, 6],
        "out_strength": [1, 2, 3, 4, 5, 6],
        "in_degree": [1, 2, 3, 4, 5, 6],
        "out_degree": [1, 2, 3, 4, 5, 6],
    }
    return dt.generateTree(data, attribute_ranges)


def check_dt_precesion(data, tree):
    correct_num = 0

    if (tree["label"] is not None):
        for item in data:
            correct_num += 1 if tree["label"] == item["label"] else 0
        return correct_num

    children = ID3.classifyByKey(data, tree["key"])

    for value, child in children.items():
        subtree = {}
        for st in tree["children"]:
            if st["value"] == value:
                subtree = st
        correct_num += check_dt_precesion(child, subtree)

    return correct_num


def show_dt_accuracy(data, tree):
    print("决策树的正确率：", check_dt_precesion(data, tree) / len(data) * 100, "%")


def generate_list(tree):
    return ID3.generateList(tree)
