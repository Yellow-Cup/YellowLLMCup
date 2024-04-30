import json
class YellowCustomer:
    def __init__(self, db, uid=""):
        self.clear(uid)
        self.db = db

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

    def collect(self):
        return {
            "UID": self.__uid,
            "EMAIL": self.__email,
            "NAME": self.__name,
            "CREATED_AT": self.__createdAt,
            "IS_LICENSE_ACTIVE": self.__isLicenseActive,
            "LICENSE_TYPE": self.__licenseType,
            "LICENSE_ACTIVATED_DATE": self.__licenseActivatedDate,
            "LICENSE_EXPIRES_DATE": self.__licenseExpiresDate,
            "CUSTOMER_JSON": self.__properties,
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

        result = self.db.retrieveData({"UID": self.uid}, self.db.customersTableName)

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
        updateDict = self.collect()
        if self.__everSaved:
            conditionDict = {"UID": self.uid}
            result = self.db.updateData(
                updateDict, conditionDict, self.db.customersTableName
            )
        else:
            result = self.db.insertData(updateDict, self.db.customersTableName)
            if result:
                self.__everSaved = True

        return result
    
    def delete(self):
        result = self.db.deleteData({"UID": self.uid}, self.db.customersTableName)
        self.clear("")

        return result

