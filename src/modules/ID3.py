import copy
import math
from json import dump

from src.modules.utils import distance


class ID3():
    def __init__(self):
        None
    
    def getAttributeRanges(self, data, attributes):
        ranges = {}
        for attr in attributes:
            ranges[attr] = set()
            for item in data:
                ranges[attr].add(item[attr])

        return ranges

    @staticmethod
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

    @staticmethod
    def generateList(tree):
        decisionList = [{}]

        def recursion_fn(tree, decisionList=[]):

            if tree["label"] is not None:
                decisionList[-1]["label"] = tree["label"]

            else:
                prefix = copy.deepcopy(decisionList[-1])

                for j, subTree in enumerate(tree["children"]):
                    if j > 0:
                        decisionList.append(copy.deepcopy(prefix))

                    decisionList[-1][tree["key"]] = subTree["value"]
                    recursion_fn(subTree, decisionList)

        recursion_fn(tree, decisionList)

        def drop_duplicates(dicts):
            res = []
            for item in dicts:
                if item not in res:
                    res.append(item)

            return res

        return drop_duplicates(decisionList)

    @staticmethod
    def checkPrecesion(data, tree):
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
            correct_num += ID3.checkPrecesion(child, subtree)

        return correct_num

    @staticmethod
    def getAttributeDistribution(data, tree):
        if (tree["label"] is not None):
            return

        children = ID3.classifyByKey(data, tree["key"])

        for value, child in children.items():
            subtree = {}
            for st in tree["children"]:
                if st["value"] == value:
                    subtree = st
    
    @staticmethod
    def saveDesicionTree(tree, to):
        with open(to, 'w') as f:
            dump(tree, f)

    def _getEntropy(self, collection, labelName="label"):
        amount = len(collection)
        devidedCollection = ID3.classifyByKey(collection, labelName)

        entropy = 0
        for kind, content in list(devidedCollection.items()):
            kindLen = len(content)
            p = kindLen / amount
            entropy -= p * math.log(p, 2)

        return entropy

    def _getEntropySum(self, devidedSet, amount=False):
        if amount == False:
            amount = 0
            for content in list(devidedSet.values()):
                amount += len(content)

        entropySum = 0
        for _set in list(devidedSet.values()):
            entropySum += len(_set) / amount * self._getEntropy(_set)

        return entropySum

    def _getPurestDeviding(self, data, attributeNames):

        bestAttr = None
        minEntropy = float("inf")
        bestDeviding = None

        for attr in attributeNames:
            devidingByAttr = ID3.classifyByKey(data, attr)
            entropySum = self._getEntropySum(devidingByAttr, len(data))
            if entropySum < minEntropy:
                bestAttr = attr
                minEntropy = entropySum
                bestDeviding = devidingByAttr

        return (bestAttr, bestDeviding, minEntropy)

    def generateTree(self, data, attributeRanges, value=None, labelName="label"):
        attributeNames = list(attributeRanges.keys())

        ys = [item[labelName] for item in data]
        ysSet = set(ys)

        # case 1: 如果只剩下一个类别，则返回该类别的标签
        if (len(ysSet) <= 1):
            return {"label": ysSet.pop(), "value": value}

        mostLabel = ys[0]
        mostNum = -1

        for y in list(ysSet):
            num = ys.count(y)
            if (num > mostNum):
                mostLabel = y
                mostNum = num

        # case 2: 如果所有属性都判断完毕，则返回 data 中样本数最多的标签
        if (len(attributeNames) == 0):
            return {"label": mostLabel, "value": value}

        sameOnAttributes = True
        for attr in attributeNames:
            divedeSet = ID3.classifyByKey(data, attr)
            if (len(divedeSet.keys()) > 1):
                sameOnAttributes = False
                break

        # case 3: 如果样本在所有属性上的取值都一致（无法进行继续决策），则同 case 2 返回样本数最多的标签
        if (sameOnAttributes):
            return {"label": mostLabel, "value": value}

        # case 4: 在剩余属性中挑选最佳划分属性，并根据该属性的每个值生成分支节点
        tree = {"children": [], "label": None, "value": value}

        bestAttr, bestDeviding, _ = self._getPurestDeviding(
            data, attributeNames)

        tree["key"] = bestAttr

        _attributeRanges = copy.deepcopy(attributeRanges)
        del _attributeRanges[bestAttr]

        for value in list(attributeRanges[bestAttr]):
            try:
                _data = bestDeviding[value]
                child = self.generateTree(_data, _attributeRanges, value)
            except KeyError:
                child = {"value": value, "label": mostLabel}

            tree["children"].append(child)

        return tree
