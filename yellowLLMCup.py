from yellowChatBot import YellowChatBot
from yellowLLMClient import YellowLLMClient
from yellowDB import YellowDB
from yellowCustomer import YellowCustomer
import roles
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
    maxPollAttempts = 10

    def __init__(self, contextCapacity=10):
        self._contextCapacity = contextCapacity
        self._failedPollAttempts = 0
        self._chatBot = YellowChatBot("Telegram")
        self._users = {}
        self._contexts = {}
        self._rolesInChats = {}
        # self._rolesInChats = {
        #     "{str chatId}":
        #         {
        #             "role": "{str role}",
        #             "isLocked": "{bool isLocked}"
        #         },
        # }

        self._LLM = YellowLLMClient()
        self._customersDB = YellowDB(environment.DBName)

    def getCustomer(self, user):
        if not user in self._users:
            self._users[user] = YellowCustomer(self._customersDB, user)
            customer = self._users[user]
            if not customer.everSaved:
                customer.name = self._chatBot.users[user].userHandler
                customer.createdAt = str(datetime.now())
                customer.save()
        else:
            customer = self._users[user]

        return customer

    def fetchMessageContext(self, message):
        contextId = "{}{}".format(message.userId, message.chatId)
        if not contextId in self._contexts:
            context = YellowContextCup(maxLength=self._contextCapacity)
            self._contexts[contextId] = context
        else:
            context = self._contexts[contextId]

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

    def getRoleInChat(self, chatId):
        if not chatId in self._rolesInChats:
            self._rolesInChats[chatId] = {
                "role": roles.defaultRole,
                "isRoleLocked": False,
            }

        return self._rolesInChats[chatId]

    def updateRoleInChat(self, chatId, role):
        isLocked = self.getRoleInChat(chatId)["isRoleLocked"]
        if not isLocked:
            self._rolesInChats[chatId]["role"] = role

        return isLocked

    def lockRoleInChat(self, chatId):
        roleData = self.getRoleInChat(chatId=chatId)
        self._rolesInChats[chatId]["isLocked"] = True

        return {
            "role": roleData["role"],
            "response": 'Locked the role: "{}"'.format(roleData["role"]),
        }

    def unlockRoleInChat(self, chatId):
        roleData = self.getRoleInChat(chatId=chatId)
        self._rolesInChats[chatId]["isLocked"] = False

        return {
            "role": roleData["role"],
            "response": 'The role "{}" is locked no more.'.format(roleData["role"]),
        }

    def run(self):
        while True:

            try:
                self._chatBot.getUpdates()
                self._failedPollAttempts = 0
            except Exception as e:
                print(e)
                self._failedPollAttempts += 1
                if self._failedPollAttempts >= self.maxPollAttempts:
                    exit()

            for msg in self._chatBot.messages:
                if msg.isHandledCode == 0:
                    # user = msg.userId
                    # customer = self.getCustomer(user)
                    context = self.getMessageContext(message=msg)
                    roleData = self.getRoleInChat(chatId=msg.chatId)
                    role = roleData["role"]
                    isRoleLocked = roleData["isRoleLocked"]
                    self.updateMessageContext(message=msg)
                    result = self._LLM.defineAgent(
                        message=msg.content,
                        context=context,
                        role=role,
                        chatId=msg.chatId,
                        isRoleLocked=isRoleLocked,
                        yellowLLMCupInstance=self,
                    )
                    response = result["response"]
                    role = result["role"]
                    self.updateRoleInChat(chatId=msg.chatId, role=role)
                    self.updateMessageContext(message=msg, LLMResponseString=response)
                    self._chatBot.sendMessage(chat=msg.chatId, message=response)
                    msg.isHandledCode = 1
                    pprint(vars(msg))
                    print(response)

            sleep(self.pollPeriodSeconds)
