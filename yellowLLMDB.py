import sqlite3
from datetime import datetime, timedelta


class SchemaAttribute:
    def __init__(self, name, typeName="TEXT",  restrictions=""):
        self._name = name
        self._typeName = typeName
        self._restrictions=restrictions
    
    @property
    def name(self):
        return self._name
    
    @property
    def restrictions(self):
        return self._restrictions
    
    @property
    def typeName(self):
        return self._typeName
    
    @property
    def schemaNotation(self):
        return "{} {} {}".format(self._name, self._typeName, self._restrictions).strip()


class SchemaPrototype:

    @property
    def schemaNotation(self):
        attributes = vars(self)
        attributesNotationList = []

        for attribute in attributes.values():
            attributesNotationList.append(attribute.schemaNotation)

        notation="({})".format(", ".join(attributesNotationList))

        return notation        


class CustomerSchema(SchemaPrototype):
    def __init__(self):
        self.id = SchemaAttribute(name="ID", typeName="INTEGER", restrictions="PRIMARY KEY")
        self.uid = SchemaAttribute(name="UID", restrictions="UNIQUE")
        self.email = SchemaAttribute(name="EMAIL")
        self.name = SchemaAttribute(name="NAME")
        self.createdAt = SchemaAttribute(name="CREATED_AT")
        self.isLicenseActive = SchemaAttribute(name="IS_LICENSE_ACTIVE")
        self.licenseType = SchemaAttribute(name="LICENSE_TYPE")
        self.licenseActivatedDate = SchemaAttribute(name="LICENCE_ACTIVATED_DATE")
        self.licenseExpiresDate = SchemaAttribute(name="LICENSE_EXPIRES_DATE")
        self.customerJSON = SchemaAttribute(name="CUSTOMER_JSON")


class TokenStatsSchema(SchemaPrototype):
    def __init__(self):
        self.id = SchemaAttribute(name="ID", typeName="INTEGER", restrictions="PRIMARY KEY")
        self.uid = SchemaAttribute(name="UID")
        self.date = SchemaAttribute(name="DATE")
        self.hour = SchemaAttribute(name="HOUR")
        self.promptTokensSpent = SchemaAttribute(name="PROMPT_TOKENS_SPENT")
        self.completionTokensSpent = SchemaAttribute(name="COMPLETION_TOKENS_SPENT")


class YellowLLMDB():
    UNCONDITIONAL_LIMIT = 100
    customersTableName = "customers"
    tokenStatsTableName = "tokens_stats" # tokens usage statistics logging
    reconnectPeriodMinutes = 5

    def __init__(self, name):
        self.name = name
        self.__openConnection()
        self.customerSchema = CustomerSchema()
        self.tokenStatsSchema = TokenStatsSchema()


    def __openConnection(self):
        self.connection = sqlite3.connect(self.name)
        self.cursor = self.connection.cursor()
        self.reconnectTime = datetime.now() + timedelta(minutes=self.reconnectPeriodMinutes)


    def closeConnection(self):
        self.connection.commit()
        self.connection.close()


    def sustainConnection(self):
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
            CREATE TABLE IF NOT EXISTS {} {};
        """.format(
            self.customersTableName,
            self.customerSchema.schemaNotation
        )

        result = self.cursor.execute(query)

        return result

    def createTokenStatsTable(self):
        query = """
            CREATE TABLE IF NOT EXISTS {} {}; 
        """.format(
            self.tokenStatsTableName,
            self.tokenStatsSchema.schemaNotation
        )

        result = self.cursor.execute(query)

        return result

    def initDB(self):
        result = self.createCustomersTable()
        result2 = self.createTokenStatsTable()
        return (result, result2)

    def dictToColumnsAndValues(self, dict):
        columnsString = ""
        valuesString = ""

        for key in dict:
            columnsString += "{}, ".format(key)
            valuesString += "'{}', ".format(dict[key])  # no .join, as non-str value break it.

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

        self.sustainConnection()

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

        self.sustainConnection()
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
            self.sustainConnection()
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
            self.sustainConnection()
            result = self.cursor.execute(query)
        except Exception as e:
            print(query)
            print(e)
            raise Exception

        return result
    