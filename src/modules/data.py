import pathlib
from matplotlib.pyplot import fill
from numpy import isnan
import numpy as np
import pandas as pd
import json
from pandas.core.frame import DataFrame


class Data():
    def __init__(self, path, name, filling) -> None:
        self.data = self._preProcessing(path)
        self._averagePrice = None
        self.fillingMethod = filling
        self.name = name

    def _preProcessing(self, path) -> DataFrame:
        extentionName = pathlib.Path(path).suffix.lower()

        if extentionName == '.csv':
            logs = pd.read_csv(path)
        elif extentionName == '.json':
            logs = pd.read_json(path)

        data = self._drop_self_lop_data(logs)
        data = self._drop_union_data(data)

        data.index = range(1, len(data)+1)

        return data

    def _drop_self_lop_data(self, data):
        return data[data["Reporter Code"] != data["Partner Code"]]

    def _drop_union_data(self, data):
        union_codes = [
            "0", "490", "899", "975", "97", "568", "839", "581", "838", "837", "577",
            0, 490, 899, 975, 97, 568, 839, 581, 838, 837, 577
        ]

        return data[~(data["Reporter Code"].isin(union_codes) | data["Partner Code"].isin(union_codes))]

    @property
    def meanPrice(self):
        # TODO get average price
        None

    @property
    def allReporters(self):

        allReporters = (
            self.data.loc[:, ["Reporter Code", "Reporter"]]
            .drop_duplicates()
        )

        allReporters.rename(
            columns={"Reporter Code": "Code", "Reporter": "Name"}, inplace=True)

        allReporters.index = range(1, len(allReporters) + 1)

        return allReporters

    @property
    def allPartners(self) -> DataFrame:

        allPartners = (
            self.data.loc[:, ["Partner Code", "Partner"]]
            .drop_duplicates()
        )

        allPartners.rename(
            columns={"Partner Code": "Code", "Partner": "Name"}, inplace=True)

        allPartners.index = range(1, len(allPartners) + 1)

        return allPartners

    @property
    def allParticipants(self) -> DataFrame:

        allReporters = self.allReporters
        allPartners = self.allPartners

        allParticipants = (
            pd.concat([allReporters, allPartners])
            .drop_duplicates()
        )

        allParticipants.index = range(1, len(allParticipants) + 1)

        return allParticipants

    @property
    def averagePrice(self):
        if self._averagePrice is None:
            logs = self._getNetData(0)
            sums = np.sum(logs, axis=0)

            self._averagePrice = sums[2] / sums[3]
        return self._averagePrice

    def getByCode(self, code):
        allParticipants = self.allParticipants
        target = allParticipants[allParticipants["Code"] == code]
        return target

    def getCountryName(self, code):
        target = self.getByCode(code)
        return target.iat[0, 1]

    def getCountryLog(self, code, flow=None, who_report=None):
        logs = self.data

        if who_report is None:
            return pd.concat([
                self.getCountryLog(code, flow, "self"),
                self.getCountryLog(code, flow, "others"),
            ]).reset_index(drop=True)

        elif who_report == "self":
            if flow is None:
                return logs[logs["Reporter Code"] == code].reset_index(drop=True)

            return logs[(logs["Reporter Code"] == code) & (logs["Trade Flow"] == flow)].reset_index(drop=True)

        elif who_report == "others":
            if flow is None:
                return logs[logs["Partner Code"] == code].reset_index(drop=True)

            elif flow == "Import":
                return logs[(logs["Partner Code"] == code) & (logs["Trade Flow"] == "Export")].reset_index(drop=True)

            elif flow == "Export":
                return logs[(logs["Partner Code"] == code) & (logs["Trade Flow"] == "Import")].reset_index(drop=True)

            else:
                raise ValueError("flow must be Import, Export or None")

        else:
            raise ValueError("who_report must be self, others or None")

    @property
    def netData(self):
        try:
            return np.loadtxt('src/data/network' + str(self.fillingMethod) + '/' + self.name + '.csv', delimiter=",")
        except OSError:
            return self._getNetData(self.fillingMethod)

    def _getNetData(self, fillingMethod=None):
        """ merge data from importer and partner and process *TradeQuantity* Nan value
        Args:
            hanlde_nan: 0 | 1 | 2,
                0: drop nan
                1: replace TradeQuantity nan with NetWeight and others 0;
                2: replace TradeQuantity nan with NetWeight and remianing nan with TradeValue/avaragePrice
        Returns: merged and processed data
        """
        if fillingMethod is None:
            fillingMethod = self.fillingMethod

        allParticipants = self.allParticipants
        tradeRecords = {}

        def getCooperationLog(u, v):
            for (partners, tradeLog) in tradeRecords.items():
                if u == partners[0] and v == partners[1]:
                    return tradeLog
            tradeRecords[(u, v)] = {
                "Trade Value": {
                    "reportFromU": 0,
                    "reportFromV": 0
                },
                "Trade Quantity": {
                    "reportFromU": 0,
                    "reportFromV": 0
                }
            }
            return tradeRecords[(u, v)]

        for row in allParticipants.itertuples():
            # selfImportLog = self.getCountryLog(row.Code, "Export", "self")
            if fillingMethod == 0:
                selfImportLog = self.getCountryLog(
                    row.Code, "Export", "self").dropna()
                for log in selfImportLog.itertuples():
                    couple_log = getCooperationLog(log._1, log._3)
                    couple_log["Trade Value"]["reportFromU"] += log._6
                    couple_log["Trade Quantity"]["reportFromU"] += log._7

            else:
                selfImportLog = self.getCountryLog(
                    row.Code, "Export", "self")
                for log in selfImportLog.itertuples():
                    couple_log = getCooperationLog(log._1, log._3)
                    if fillingMethod == 1:
                        couple_log["Trade Value"]["reportFromU"] += log._6
                        couple_log["Trade Quantity"]["reportFromU"] += \
                            (0 if isnan(log.NetWeight) else log.NetWeight) \
                            if isnan(log._7) else log._7
                    if fillingMethod == 2:
                        couple_log["Trade Value"]["reportFromU"] += log._6
                        couple_log["Trade Quantity"]["reportFromU"] += \
                            ((log._6 / self.averagePrice) if isnan(log.NetWeight) else log.NetWeight) \
                            if isnan(log._7) else log._7

            # selfExportLog = self.getCountryLog(row.Code, "Import", "self")
            if fillingMethod == 0:
                selfImportLog = self.getCountryLog(
                    row.Code, "Import", "self").dropna()
                for log in selfImportLog.itertuples():
                    couple_log = getCooperationLog(log._3, log._1)
                    couple_log["Trade Value"]["reportFromU"] += log._6
                    couple_log["Trade Quantity"]["reportFromU"] += log._7

            else:
                selfImportLog = self.getCountryLog(
                    row.Code, "Import", "self")
                for log in selfImportLog.itertuples():
                    couple_log = getCooperationLog(log._3, log._1)
                    if fillingMethod == 1:
                        couple_log["Trade Value"]["reportFromV"] += log._6
                        couple_log["Trade Quantity"]["reportFromV"] += \
                            (0 if isnan(log.NetWeight) else log.NetWeight) \
                            if isnan(log._7) else log._7
                    if fillingMethod == 2:
                        couple_log["Trade Value"]["reportFromV"] += log._6
                        couple_log["Trade Quantity"]["reportFromV"] += \
                            ((log._6 / self.averagePrice) if isnan(log.NetWeight) else log.NetWeight) \
                            if isnan(log._7) else log._7

        def get_mean(arr):
            if arr[0] != 0 and arr[1] != 0:
                return int(sum(arr) / 2)
            else:
                return max(arr)

        for key, value in tradeRecords.items():
            tradeRecords[key]["Trade Value"] =\
                get_mean(list(value["Trade Value"].values()))
            tradeRecords[key]["Trade Quantity"] =\
                get_mean(list(value["Trade Quantity"].values()))

        netData = [[k[0], k[1], v['Trade Value'], v['Trade Quantity']]
                   for k, v in tradeRecords.items() if v['Trade Quantity'] > 0]
        np.savetxt('src/data/network' + str(fillingMethod) +
                   '/' + self.name + '.csv', netData, delimiter=',')

        return netData

    def save_gephi_edges(self):
        data = self.netData

        tableHead = ["source", "target", "weight"]

        tableBody = [
            [
                str(int(v[0])),
                str(int(v[1])),
                str(int(v[3]))
            ] for v in data]
        table = [tableHead] + tableBody
        with open('src/data/network' + str(self.fillingMethod) +
                  '/' + self.name + '-gephi-edges.csv', 'w', encoding="utf8") as f:
            csv_txt = "\n".join([','.join(line) for line in table])
            f.write(csv_txt)

    def save_gephi_nodes(self):
        data = self.netData

        tableHead = ["id", "label"]

        codes = set()
        for log in data:
            codes.add(int(log[0]))
            codes.add(int(log[1]))

        tableBody = [
            [
                str(code),
                "\"" + self.getCountryName(code) + "\""
            ] for code in codes]
        table = [tableHead] + tableBody
        with open('src/data/network' + str(self.fillingMethod) +
                  '/' + self.name + '-gephi-nodes.csv', 'w', encoding="utf8") as f:
            csv_txt = "\n".join([','.join(line) for line in table])
            f.write(csv_txt)

    def save_csv_table(self):
        data = self.netData
        tableHead = ["SN", "Exporter Code", "Exporter",
                     "Importer Code", "Importer", "Trade Quantity (kg)"]

        tableBody = [
            [
                str(i + 1),
                str(int(v[0])), "\"" + self.getCountryName(int(v[0])) + "\"",
                str(int(v[1])), "\"" + self.getCountryName(int(v[1])) + "\"",
                str(int(v[3]))
            ] for i, v in enumerate(data)]
        table = [tableHead] + tableBody
        with open('src/data/network' + str(self.fillingMethod) +
                  '/' + self.name + '-table.csv', 'w', encoding="utf8") as f:
            csv_txt = "\n".join([','.join(line) for line in table])
            f.write(csv_txt)
