from yellowChatBot import YellowChatBot
from yellowGPTClient import YellowGPTClient
from yellowDB import YellowDB
from yellowCustomer import YellowCustomer
from time import sleep
import environment
from datetime import datetime
from pprint import pprint


class YellowContextCup:

    def __init__(self, maxLength=10):

        self._maxLength = maxLength
        self._storage = []
        self._lastFetchDate = 0

    def store(self, itemString):

        self._storage.append(str(itemString))
        if len(self._storage) > self._maxLength:
            del self._storage[0]

    @property
    def context(self):
        return "\n".join(self._storage)

    @property
    def storage(self):
        return self._storage

    @property
    def lastFetchDate(self):
        return self._lastFetchDate

    @lastFetchDate.setter
    def lastFetchDate(self, update):
        self._lastfetchDate = update


class YellowLLMCup:

    pollPeriodSeconds = 3

    def __init__(self, contextCapacity=10):
        self._contextCapacity = contextCapacity
        self.chatBot = YellowChatBot("Telegram")
        self.users = {}
        self.contexts = {}
        self.GPT = YellowGPTClient()
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

    def fetchMessageContext(self, message):
        contextId = "{}{}".format(message.userId, message.chatId)
        if not contextId in self.contexts:
            context = YellowContextCup(maxLength=self._contextCapacity)
            self.contexts[contextId] = context
        else:
            context = self.contexts[contextId]

        context.lastFetchDate = message.date

        return context

    def getMessageContext(self, message):
        context = self.fetchMessageContext(message)

        return context.context

    def updateMessageContext(self, message, LLMResponseString=None):
        context = self.fetchMessageContext(message)
        if LLMResponseString is None:
            context.store(message.content)
        else:
            context.store(LLMResponseString)

    def run(self):
        while True:
            self.chatBot.getUpdates()

            for msg in self.chatBot.messages:
                if msg.isHandledCode == 0:
                    user = msg.userId
                    # customer = self.getCustomer(user)
                    context = self.getMessageContext(msg)
                    self.updateMessageContext(msg)
                    response = self.GPT.defineAgent(message=msg.content, context=context)
                    self.updateMessageContext(msg, LLMResponseString=response)
                    self.chatBot.sendMessage(chat=msg.chatId, message=response)
                    msg.isHandledCode = 1
                    pprint(vars(msg))

            sleep(self.pollPeriodSeconds)
