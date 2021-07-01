import pandas as pd
from pandas.core.frame import DataFrame


class Data():
    def __init__(self, path) -> None:
        self.data = self._preProcessing(path)
        self._allReporters = None
        self._allPartners = None
        self._allParticipants = None

    def _preProcessing(self, path) -> DataFrame:
        resourceData = pd.read_csv(path)
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
