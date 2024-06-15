from yellowChatBot import YellowChatBot
from yellowLLMClient import YellowLLMClient
from yellowLLMDB import YellowLLMDB
from yellowCustomer import YellowCustomer
from yellowLLMStats import YellowLLMStats
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

    def clear(self):
        self._storage.clear()

    @property
    def lastFetchDate(self):
        return self._lastFetchDate

    @lastFetchDate.setter
    def lastFetchDate(self, update):
        self._lastfetchDate = update


class YellowLLMCup:

    pollPeriodSeconds = 1
    maxPollAttempts = 10
    agentRole = "Agent"

    def __init__(self, contextCapacity=5):
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

        self._DB = YellowLLMDB(environment.DBName)
        self._LLM = YellowLLMClient(self._DB)
        self._LLMStats = YellowLLMStats(self._DB)

    def getCustomer(self, user):
        if not user in self._users:
            self._users[user] = YellowCustomer(self._DB, user)
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

    def clearContext(self, message):
        context = self.fetchMessageContext(message)
        context.clear()

        return {
            "role": self.agentRole,
            "response": "The context is cleared; new discussion from here on.",
        }

    def getRoleInChat(self, message):
        if not message.chatId in self._rolesInChats:
            self._rolesInChats[message.chatId] = {
                "role": roles.defaultRole,
                "isRoleLocked": False,
            }

        return self._rolesInChats[message.chatId]

    def updateRoleInChat(self, message, role):
        isLocked = self.getRoleInChat(message=message)["isRoleLocked"]
        if not isLocked:
            self._rolesInChats[message.chatId]["role"] = role

        return isLocked

    def lockRoleInChat(self, message):
        roleData = self.getRoleInChat(message=message)
        self._rolesInChats[message.chatId]["isLocked"] = True

        return {
            "role": self.agentRole,
            "response": 'Locked the role: "{}"'.format(roleData["role"]),
        }

    def unlockRoleInChat(self, message):
        roleData = self.getRoleInChat(message=message)
        self._rolesInChats[message.chatId]["isLocked"] = False

        return {
            "role": self.agentRole,
            "response": 'The role "{}" is locked no more.'.format(roleData["role"]),
        }

    def run(self):
        pause = self.pollPeriodSeconds
        pauseLimit = pause * 10

        while True:

            try:
                self._chatBot.getUpdates()
                self._failedPollAttempts = 0
            except Exception as e:
                print(e)
                self._failedPollAttempts += 1
                print(
                    "Chat polling fail {} of {} attempts".format(
                        self._failedPollAttempts, self.maxPollAttempts
                    )
                )
                if self._failedPollAttempts >= self.maxPollAttempts:
                    exit()

            updatesReceived = False

            for msg in self._chatBot.messages:
                if msg.isHandledCode == 0:
                    updatesReceived = True
                    user = msg.userId
                    customer = self.getCustomer(user)
                    context = self.getMessageContext(message=msg)
                    roleData = self.getRoleInChat(message=msg)
                    role = roleData["role"]
                    isRoleLocked = roleData["isRoleLocked"]
                    self.updateMessageContext(message=msg)

                    result = self._LLM.defineAgent(
                        message=msg,
                        prompt=msg.content,
                        context=context,
                        role=role,
                        chatId=msg.chatId,
                        isRoleLocked=isRoleLocked,
                        yellowLLMCupInstance=self,
                    )
                    
                    response = result["response"]
                    role = result["role"]

                    if "tokensUsage" in result:
                        tokensUsed = result["tokensUsage"]
                    else:
                        tokensUsed = self._LLM.tokenStatsDefault

                    tokenStatsDict = {
                        self._LLMStats.schema.promptTokensSpent.name: tokensUsed[
                            self._LLM.promptTokensSpentKey
                        ],
                        self._LLMStats.schema.completionTokensSpent.name: tokensUsed[
                            self._LLM.completionTokensSpentKey
                        ],
                    }

                    self._LLMStats.updateTokenStats(
                        UID=customer.uid,
                        timestamp=msg.date,
                        tokenStatsDict=tokenStatsDict,
                    )

                    if role != self.agentRole:
                        self.updateRoleInChat(message=msg, role=role)
                        self.updateMessageContext(message=msg, LLMResponseString=response)
                    self._chatBot.sendMessage(chat=msg.chatId, message=response)
                    msg.isHandledCode = 1
                    self._DB.sustainConnection()

                    pprint(vars(msg))
                    print(response)
                    print(datetime.fromtimestamp(msg.date))
                    print(tokensUsed)

            if updatesReceived:
                pause = self.pollPeriodSeconds
            else:
                if pause < pauseLimit:
                    pause += pause

            sleep(pause)
