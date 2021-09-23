import pathlib
import pandas as pd
from pandas.core.frame import DataFrame


class Data():
    def __init__(self, path) -> None:
        self.data = self._preProcessing(path)
        self._allReporters = None
        self._allPartners = None
        self._allParticipants = None
        self._mergedData = None

    def _preProcessing(self, path) -> DataFrame:
        extentionName = pathlib.Path(path).suffix.lower()
        if extentionName == '.csv':
            resourceData = pd.read_csv(path)
        elif extentionName == '.json':
            resourceData = pd.read_json(path)
        data = (
            resourceData[resourceData["Partner Code"] != 0]
            .loc[:, ["Reporter Code", "Reporter", "Partner Code", "Partner", "Trade Flow", "Trade Value (US$)"]]
        )
        return data

    def getAllReporters(self) -> DataFrame:
        if (self._allReporters is not None):
            return self._allReporters

        self._allReporters = (
            self.data.loc[:, ["Reporter Code", "Reporter"]]
            .drop_duplicates()
        )

        self._allReporters.rename(
            columns={"Reporter Code": "Code", "Reporter": "name"}, inplace=True)

        return self._allReporters

    def getAllPartners(self) -> DataFrame:
        if (self._allPartners is not None):
            return self._allPartners

        self._allPartners = (
            self.data.loc[:, ["Partner Code", "Partner"]]
            .drop_duplicates()
        )

        self._allPartners.rename(
            columns={"Partner Code": "Code", "Partner": "name"}, inplace=True)

        return self._allPartners

    def getAllParticipants(self) -> DataFrame:
        if (self._allParticipants is not None):
            return self._allParticipants

        allReporters = self.getAllReporters()
        allPartners = self.getAllPartners()

        self._allParticipants = (
            pd.concat([allReporters, allPartners])
            .drop_duplicates()
        )

        return self._allParticipants

    def getByCode(self, code):
        allParticipants = self.getAllParticipants()
        target = allParticipants[allParticipants["Code"] == code]
        return target

    def getCountryName(self, code):
        target = self.getByCode(code)
        return target.iat[0, 1]

    def _getGroupLog(self, type, by):
        allImportLog = pd.concat([
            self.data[self.data["Trade Flow"] == "Import"],
            self.data[self.data["Trade Flow"] == "Re-Import"]
        ])

        allExportLog = pd.concat([
            self.data[self.data["Trade Flow"] == "Export"],
            self.data[self.data["Trade Flow"] == "Re-Export"]
        ])

        if(type == "Import"):
            return allImportLog.groupby(by)

        if(type == "Export"):
            return allExportLog.groupby(by)

    def getCountryLog(self, code, type, repoter="self"):
        if (repoter == "self"):
            return (self._getGroupLog(type, "Reporter Code")).get_group(code)
        else:
            return (self._getGroupLog(type, "Partner Code")).get_group(code)

    def getMergedData(self):
        if (self._mergedData is not None):
            return self._mergedData
        allParticipants = self.getAllParticipants()
        tradeRecords = {}

        def getCooperationLog(u, v):
            for (partners, tradeLog) in tradeRecords.items():
                if u == partners[0] and v == partners[1]:
                    return tradeLog
            tradeRecords[(u, v)] = {"Import": 0, "Export": 0}
            return tradeRecords[(u, v)]

        for row in allParticipants.itertuples():
            try:
                selfImportLog = self.getCountryLog(row.Code, "Import", "self")
                for log in selfImportLog.itertuples():
                    getCooperationLog(log._3, log._1)["Import"] += log._6
            except KeyError:
                None

            try:
                exportPartnerLog = self.getCountryLog(
                    row.Code, "Export", "partner")
                for log in exportPartnerLog.itertuples():
                    getCooperationLog(log._1, log._3)["Export"] += log._6
            except KeyError:
                None

        for key, value in tradeRecords.items():
            tradeRecords[key] = int((value["Import"] + value["Export"]) / 2)

        self._mergedData = tradeRecords

        return tradeRecords
