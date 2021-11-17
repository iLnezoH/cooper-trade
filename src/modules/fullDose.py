import json
from os import replace
import random
import numpy as np
import math
from src.modules.ID3 import ID3

rng = np.random.default_rng()


class FullDoseDT():
    def __init__(self, years=None, filling=2) -> None:
        if years is None:
            self.years = [
                '2011', '2012', '2013', '2014', '2015',
                '2016', '2017', '2018', '2019', '2020'
            ]
        else:
            self.years = [str(y) for y in years]
        self.fillingMethod = filling
        self.data, self.train_data, self.validate_data, self.test_data = self._init_data()
        self.decision_tree = None

    def _init_data(self):
        file_name = ','.join(self.years)
        try:
            with open('src/data/network' + str(self.fillingMethod) + '/' + file_name + '-nodes.json') as f:
                data = json.load(f)
        except:
            data = []
            for y in self.years:
                with open('src/data/network' + str(self.fillingMethod) + '/' + y + '-nodes.json') as f:
                    data += json.load(f)
            with open('src/data/network' + str(self.fillingMethod) + '/' + file_name + '-nodes.json', 'w') as f:
                json.dump(data, f)

        data = np.array(data)

        try:
            with open('src/data/network' + str(self.fillingMethod) + '/' + file_name + '-train-nodes.json') as f:
                train_data = json.load(f)
            with open('src/data/network' + str(self.fillingMethod) + '/' + file_name + '-validate-nodes.json') as f:
                validate_data = json.load(f)
            with open('src/data/network' + str(self.fillingMethod) + '/' + file_name + '-test-nodes.json') as f:
                test_data = json.load(f)
        except:
            train_index = rng.choice(
                np.arange(len(data)),
                math.ceil(len(data) * 0.6),
                replace=False
            )
            remain_index = np.delete(np.arange(len(data)), train_index)
            validate_index = rng.choice(
                np.arange(len(remain_index)),
                math.ceil(len(remain_index)/2),
                replace=False
            )
            test_index = np.delete(
                np.arange(len(remain_index)), validate_index)
            train_data = data[train_index]
            validate_data = data[remain_index[validate_index]]
            test_data = data[test_index]
            with open('src/data/network' + str(self.fillingMethod) + '/' + file_name + '-train-nodes.json', 'w') as f:
                json.dump(list(train_data), f)
            with open('src/data/network' + str(self.fillingMethod) + '/' + file_name + '-validate-nodes.json', 'w') as f:
                json.dump(list(validate_data), f)
            with open('src/data/network' + str(self.fillingMethod) + '/' + file_name + '-test-nodes.json', 'w') as f:
                json.dump(list(test_data), f)

        return data, train_data, validate_data, test_data

    def train(self, label_name="E"):
        dt = ID3()
        attribute_ranges = {
            "IS": [1, 2, 3, 4, 5, 6],
            "OS": [1, 2, 3, 4, 5, 6],
            "BC": [1, 2, 3, 4, 5, 6],
            "DC": [1, 2, 3, 4, 5, 6],
            "CC": [1, 2, 3, 4, 5, 6],
        }
        '''
        for name, value in self.attributes.items():
            if name == label_name:
                continue
            attribute_ranges[name] = [i+1 for i in range(value['layer'])]
        '''

        tree = dt.generateTree(self.train_data, attribute_ranges)
        ID3.saveDesicionTree(tree, 'outputs/tree-' +
                             ','.join(self.years) + '.json')
        self.decision_tree = tree

    def test(self, data=None, error_range=0):
        if data is None:
            data = self.test_data
        print("决策树的正确率：", ID3.checkPrecesion(
            data, self.decision_tree, error_range=error_range) / len(data) * 100, "%")

    @property
    def decision_list(self):
        return ID3.generateList(self.decision_tree)

    def cut(self):
        ID3.cut(self.decision_tree, self.decision_tree, self.validate_data)
        ID3.saveDesicionTree(self.decision_tree, 'outputs/tree-' +
                             ','.join(self.years) + '.json')
