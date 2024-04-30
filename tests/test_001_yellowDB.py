import os
from yellowLLMCup.yellowDB import YellowDB
from yellowLLMCup.yellowCustomer import YellowCustomer
from yellowLLMCup import environment

class TestDB:

    testCustomerId = "_testCustomer"
    testCustomerEmail = "_testmail@_mail.com"


    def test_00_DBInit(self):
        with YellowDB(environment.DBName) as db:
            db.initDB()

    def test_01_AddCustomer(self):
        with YellowDB(environment.DBName) as db:
            customer = YellowCustomer(db)
            customer.uid = self.testCustomerId
            customer.save()
            assert customer.everSaved

    def test_02_ModifyCustomer(self):
        with YellowDB(environment.DBName) as db:
            customer = YellowCustomer(db, self.testCustomerId)
            assert customer.everSaved
            customer.email = self.testCustomerEmail
            customer.save()
        
        with YellowDB(environment.DBName) as db1:
            customer1 = YellowCustomer(db1, self.testCustomerId)
            assert customer1.email == self.testCustomerEmail

    def test_03_DeleteCustomer(self):
        with YellowDB(environment.DBName) as db:
            customer = YellowCustomer(db, self.testCustomerId)
            assert customer.everSaved
            customer.email = self.testCustomerEmail
            customer.delete()

            assert customer.uid == ""

    def test_CleanUp(self):
        with YellowDB(environment.DBName) as db:
            name = db.name
        os.remove(name)
