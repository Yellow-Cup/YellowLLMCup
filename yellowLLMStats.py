from datetime import datetime
from yellowLLMDB import TokenStatsSchema


class YellowLLMStats:

    def __init__(self, db):
        self.__db = db
        self.__schema = TokenStatsSchema()

    @property
    def schema(self):
        return self.__schema

    def __getTimeDict(self, timestamp):
        theTime = datetime.fromtimestamp(timestamp)
        dateStr = str(theTime.date())
        hour = theTime.hour

        return {self.__schema.date.name: dateStr, self.__schema.hour.name: hour}

    def updateTokenStats(self, UID, timestamp, tokenStatsDict):
        conditions = self.__getTimeDict(timestamp)
        conditions[self.__schema.uid.name] = UID
        updateStats = {}

        ptsKey = self.__schema.promptTokensSpent.name
        ctsKey = self.__schema.completionTokensSpent.name

        updateStats[ptsKey] = tokenStatsDict[ptsKey]
        updateStats[ctsKey] = tokenStatsDict[ctsKey]

        check = self.__db.retrieveData(conditions, self.__db.tokenStatsTableName)
        if len(check) > 0:
            promptTokensSpent = int(check[0][4])
            completionTokensSpent = int(check[0][5])
            updateStats[ptsKey] += promptTokensSpent
            updateStats[ctsKey] += completionTokensSpent
            self.__db.updateData(
                newDataDictionary=updateStats,
                conditionDictionary=conditions,
                tableName=self.__db.tokenStatsTableName,
            )
        else:
            self.__db.insertData(
                dataDictionary={**conditions, **updateStats},
                tableName=self.__db.tokenStatsTableName,
            )

        return True
