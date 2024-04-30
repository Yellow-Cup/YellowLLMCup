from yellowChatBot import YellowChatBot
from yellowGPTClient import YellowGPTClient
from yellowDB import YellowDB
from yellowCustomer import YellowCustomer
from time import sleep
import environment
from datetime import datetime
from pprint import pprint


class YellowContextCup:

    def __init__(self):
        pass

class YellowLLMCup:

    pollPeriodSeconds = 3

    def __init__(self):
        self.chatBot = YellowChatBot("Telegram")
        self.users = {}
            # {
            #     userId: {
            #         "data": YellowCustomer(),
            #         "contextCup": {
            #             chatId: "text"
            #         }
            #     }
            # }
        # self.GPT = YellowGPTClient()
        self.customersDB = YellowDB(environment.DBName)

    def getCustomer(self, user):
        if not user in self.users:
            self.users[user] = YellowCustomer(self.customersDB, user)
            customer = self.users[user]
            if not customer.everSaved:
                customer.name = self.chatBot.users[user].userHandler
                customer.createdAt = str(datetime.now())
                customer.save()
        else:
            customer = self.users[user]

        return customer
    
    def getMessageContext(self, message):
        context = ""
        chat = self.chatBot.chats[message.chatId]
        for msg in chat.messages:
            if msg.userId == message.userId:
                context += msg.content + "\n"
        
        return context

    def run(self):
        while True:
            self.chatBot.getUpdates()
            
            print("---MESSAGES---")
            for msg in self.chatBot.messages:
                if msg.isHandledCode == 0:
                    # pprint(vars(msg))
                    user = msg.userId
                    customer = self.getCustomer(user)
                    # pprint(vars(customer))
                    context = self.getMessageContext(msg)
                    res1=self.chatBot.sendMessage("The context: ", msg.chatId)
                    res2=self.chatBot.sendMessage(context, msg.chatId)
                    msg.isHandledCode = 1
            print("=====")

            

            print("---CHATS---")
            for chat in self.chatBot.chats:
                pprint(vars(self.chatBot.chats[chat]))
            print("=====")
            print("---USERS---")
            for user in self.chatBot.users:
                print(user)
                pprint(vars(self.chatBot.users[user]))
            print("=====")

            sleep(self.pollPeriodSeconds)
