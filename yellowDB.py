import sqlite3
from datetime import datetime, timedelta

class YellowDB():
    UNCONDITIONAL_LIMIT = 100
    customersTableName = "customers"
    reconnectPeriodMinutes = 5

    def __init__(self, name):
        self.name = name
        self.__openConnection()


    def __openConnection(self):
        self.connection = sqlite3.connect(self.name)
        self.cursor = self.connection.cursor()
        self.reconnectTime = datetime.now() + timedelta(minutes=self.reconnectPeriodMinutes)


    def closeConnection(self):
        self.connection.commit()
        self.connection.close()


    def __sustainConnection(self):
        if datetime.now() > self.reconnectTime:
            self.closeConnection()
            self.__openConnection()

            return True
        return False


    def __enter__(self):
        self.__openConnection()
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self.closeConnection()

    def createCustomersTable(self):
        query = """
            CREATE TABLE IF NOT EXISTS {} 
                (ID integer primary key, UID UNIQUE, EMAIL, NAME, CREATED_AT, IS_LICENSE_ACTIVE,
                LICENSE_TYPE, LICENSE_ACTIVATED_DATE, LICENSE_EXPIRES_DATE, CUSTOMER_JSON);
        """.format(
            self.customersTableName
        )

        result = self.cursor.execute(query)

        return result

    def initDB(self):
        result = self.createCustomersTable()
        return result

    def dictToColumnsAndValues(self, dict):
        columnsString = ""
        valuesString = ""

        for key in dict:
            columnsString += "{}, ".format(key)
            valuesString += "'{}', ".format(dict[key])

        return columnsString[:-2], valuesString[:-2]

    def dictToCondition(self, dict):
        conditionString = ""

        for key in dict:
            if str(dict[key])[0] == "!":
                conditionString += "({0} <> '{1}' OR {0} IS NULL) AND ".format(key, dict[key][1:])
            else:
                conditionString += "{} = '{}' AND ".format(key, dict[key])

        return conditionString[:-5]

    def dictToUpdate(self, dict):
        updateString = ""

        for key in dict:
            updateString += "{} = '{}', ".format(key, dict[key])

        return updateString[:-2]

    def insertData(self, dataDictionary, tableName):
        """
        query = "INSERT INTO {} ({}) VALUES ({});".format(tableName, columns, values)
        """

        columns, values = self.dictToColumnsAndValues(dataDictionary)
        query = "INSERT INTO {} ({}) VALUES ({});".format(tableName, columns, values)

        self.__sustainConnection()

        try:
            result = self.cursor.execute(query)
        except Exception as e:
            print(query)
            print(e)
            raise Exception

        return result

    def retrieveData(self, conditionDictionary, tableName):
        """
        query = "SELECT * FROM {} WHERE {};".format(tableName, condition)
        """
        if len(conditionDictionary) > 0:
            condition = self.dictToCondition(conditionDictionary)
        else:
            condition = "1 LIMIT {}".format(self.UNCONDITIONAL_LIMIT)

        query = "SELECT * FROM {} WHERE {};".format(tableName, condition)

        self.__sustainConnection()
        result = self.cursor.execute(query)

        try:
            return result.fetchall()
        except Exception as e:
            print(query)
            print(e)
            raise Exception


    def updateData(self, newDataDictionary, conditionDictionary, tableName):
        """
        query = "UPDATE {} SET {} WHERE {};".format(tableName, newData, condition)
        """
        newData = self.dictToUpdate(newDataDictionary)

        if len(conditionDictionary) > 0:
            condition = self.dictToCondition(conditionDictionary)
        else:
            condition = "1 LIMIT {}".format(self.UNCONDITIONAL_LIMIT)

        try:
            query = "UPDATE {} SET {} WHERE {};".format(tableName, newData, condition)
            self.__sustainConnection()
            result = self.cursor.execute(query)
        except Exception as e:
            print(query)
            print(e)
            raise Exception

        return result


    def deleteData(self, conditionDictionary, tableName):
        """
            query = "DELETE FROM {} WHERE {};".format(tableName, condition)
        """

        if len(conditionDictionary) > 0:
            condition = self.dictToCondition(conditionDictionary)
        else:
            print("No condition set")
            raise Exception

        try:
            query = "DELETE FROM {} WHERE {};".format(tableName, condition)
            self.__sustainConnection()
            result = self.cursor.execute(query)
        except Exception as e:
            print(query)
            print(e)
            raise Exception

        return result
    