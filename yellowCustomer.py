import json
from yellowLLMDB import CustomerSchema
class YellowCustomer:
    def __init__(self, db, uid=""):
        self.clear(uid)
        self.db = db
        self._schema = CustomerSchema()

        if uid != "":
            self.__fetchData()

        return None
    
    def clear(self, uid):
        self.__uid = uid
        self.__email = ""
        self.__name = ""
        self.__createdAt = ""
        self.__isLicenseActive = False
        self.__licenseType = ""
        self.__licenseActivatedDate = ""
        self.__licenseExpiresDate = ""
        self.__properties = {}
        self.__everSaved = False

        return None

        # self.id = SchemaAttribute(name="ID", typeName="INTEGER", restrictions="PRIMARY KEY")
        # self.uid = SchemaAttribute(name="UID", restrictions="UNIQUE")
        # self.email = SchemaAttribute(name="EMAIL")
        # self.name = SchemaAttribute(name="NAME")
        # self.createdAt = SchemaAttribute(name="CREATED_AT")
        # self.isLicenceActive = SchemaAttribute(name="IS_LICENSE_ACTIVE")
        # self.licenseType = SchemaAttribute(name="LICENSE_TYPE")
        # self.licenseActivatedDate = SchemaAttribute(name="LICENCE_ACTIVATED_DATE")
        # self.licenseExpiresDate = SchemaAttribute(name="LICENSE_EXPIRES_DATE")
        # self.customerJSON = SchemaAttribute(name="CUSTOMER_JSON")

    def __collect(self):
        return {
            self._schema.uid.name: self.__uid,
            self._schema.email.name: self.__email,
            self._schema.name.name: self.__name,
            self._schema.createdAt.name: self.__createdAt,
            self._schema.isLicenseActive.name: self.__isLicenseActive,
            self._schema.licenseType.name: self.__licenseType,
            self._schema.licenseActivatedDate.name: self.__licenseActivatedDate,
            self._schema.licenseExpiresDate.name: self.__licenseExpiresDate,
            self._schema.customerJSON.name: self.__properties,
        }

    @property
    def everSaved(self):
        return self.__everSaved
    
    @everSaved.setter
    def everSaved(self, input):
        print("everSaved is a r/o parameter")
        return False

    @property
    def uid(self):
        return self.__uid

    @uid.setter
    def uid(self, newUid):
        if newUid != "":
            self.__uid = newUid
            return True
        else:
            return False

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, newEmail):
        if newEmail != "":
            self.__email = newEmail
            return True
        else:
            return False

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, newName):
        if newName != "":
            self.__name = newName
            return True
        else:
            return False

    @property
    def createdAt(self):
        return self.__createdAt

    @createdAt.setter
    def createdAt(self, newCreatedAt):
        if newCreatedAt != "":
            self.__createdAt = newCreatedAt
            return True
        else:
            return False

    @property
    def isLicenseActive(self):
        return self.__isLicenseActive

    @isLicenseActive.setter
    def isLicenseActive(self, newIsLicenseActive):
        self.__isLicenseActive = newIsLicenseActive
        return True

    @property
    def licenseType(self):
        return self.__licenseType

    @licenseType.setter
    def licenseType(self, newLicenseType):
        if newLicenseType != "":
            self.__licenseType = newLicenseType
            return True
        else:
            return False

    @property
    def licenseActivatedDate(self):
        return self.__licenseActivatedDate

    @licenseActivatedDate.setter
    def licenseActivatedDate(self, newLicenseActivatedDate):
        if newLicenseActivatedDate != "":
            self.__licenseActivatedDate = newLicenseActivatedDate
            return True
        else:
            return False

    @property
    def licenseExpiresDate(self):
        return self.__licenseExpiresDate

    @licenseExpiresDate.setter
    def licenseExpiresDate(self, newLicenseExpiresDate):
        if newLicenseExpiresDate != "":
            self.__licenseExpiresDate = newLicenseExpiresDate
            return True
        else:
            return False

    @property
    def properties(self):
        return self.__properties

    @properties.setter
    def properties(self, newProperties):
        if len(newProperties) > 0:
            self.__properties = newProperties
            return True
        else:
            return False

    def __fetchData(self):
        if self.uid == "":
            return False

        result = self.db.retrieveData({self._schema.uid.name: self.uid}, self.db.customersTableName)

        if result:
            data = result[0]
            self.__everSaved = True
            self.uid = (data[1])
            self.email = (data[2])
            self.name = (data[3])
            self.createdAt = (data[4])
            self.isLicenseActive = (data[5] == 'True')
            self.licenseType = (data[6])
            self.licenseActivatedDate = (data[7])
            self.licenseExpiresDate = (data[8])
            self.properties = (json.loads(data[9]))
        else:
            return False
        
        return result

    def save(self):
        updateDict = self.__collect()
        if self.__everSaved:
            conditionDict = {self._schema.uid.name: self.uid}
            result = self.db.updateData(
                updateDict, conditionDict, self.db.customersTableName
            )
        else:
            result = self.db.insertData(updateDict, self.db.customersTableName)
            if result:
                self.__everSaved = True

        return result
    
    def delete(self):
        result = self.db.deleteData({self._schema.uid.name: self.uid}, self.db.customersTableName)
        self.clear("")

        return result

