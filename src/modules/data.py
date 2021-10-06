import pathlib
import pandas as pd
from pandas.core.frame import DataFrame


class Data():
    def __init__(self, path) -> None:
        self.data = self._preProcessing(path)
        self._allParticipants = None
        self._mergedData = None

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
            "0", "490", "899", "975", "97", "568",
            0, 490, 899, 975, 97, 568
        ]

        return data[~(data["Reporter Code"].isin(union_codes) | data["Partner Code"].isin(union_codes))]

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

    def getMergedData(self):
        if (self._mergedData is not None):
            return self._mergedData
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
            try:
                selfImportLog = self.getCountryLog(row.Code, "Export", "self")
                for log in selfImportLog.itertuples():
                    _log = getCooperationLog(log._1, log._3)
                    _log["Trade Value"]["reportFromU"] += log._6
                    _log["Trade Quantity"]["reportFromU"] += log._7
            except KeyError:
                None

            try:
                selfExportLog = self.getCountryLog(row.Code, "Import", "self")
                for log in selfExportLog.itertuples():
                    _log = getCooperationLog(log._3, log._1)
                    _log["Trade Value"]["reportFromV"] += log._6
                    _log["Trade Quantity"]["reportFromV"] += log._7
            except KeyError:
                None

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

        self._mergedData = tradeRecords

        return tradeRecords
