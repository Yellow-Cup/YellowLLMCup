import environment
import requests

MAX_STORED_MESSAGES_PER_USER = 256
MAX_STORED_MESSAGES_PER_CHAT = 256
MAX_STORED_MESSAGES_PER_BOT = 65536


def YellowChatBot(bot="Telegram", *args, **kwargs):
    """
        .chats
            .users
            .messages
        .users
            .messages
        .messages
            .chat
            .user

    def chats(self):
        return self._chats

    def addChat(self, chat):
        self._chats[chat.id] = chat

    def getChat(self, chatId):
        if chatId in self._chats:
            return self._chats[chatId]
        else:
            return None

    def getUpdates(self):
        pass

    def sendMessage(self, chat, message):
        pass
            
    """
    if bot == "Telegram":
        return YellowTelegram(*args, **kwargs)
    else:
        return None


class YellowMessagesCarrierMixin:

    def __init__(self, maxMessages=1024, **kwargs):
        self._maxMessages = maxMessages
        self._messages = []
        super().__init__(**kwargs)

    @property
    def messages(self):
        return self._messages

    def addMessage(self, message):
        self._messages.append(message)
        if len(self._messages) > self._maxMessages:
            del self._messages[0]

    def purgeMessages(self):
        self._messages = []


class YellowUsersCarrierMixin:

    def __init__(self, **kwargs):
        self._users = {}
        super().__init__(**kwargs)

    @property
    def users(self):
        return self._users

    def addUser(self, user):
        self._users[user.id] = user

    def getUser(self, userId):
        if userId in self._users:
            return self._users[userId]
        else:
            return None


class YellowChatMessage:

    def __init__(self, messageId, messageDate, content):
        self._id = messageId
        self._date = messageDate
        self._content = content
        self._isHandledCode = 0

        self._chatId = None
        self._userId = None

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        return self._date

    @property
    def content(self):
        return self._content

    @property
    def chatId(self):
        return self._chatId

    @chatId.setter
    def chatId(self, theId):
        self._chatId = theId

    @property
    def userId(self):
        return self._userId

    @userId.setter
    def userId(self, theId):
        self._userId = theId

    @property
    def isHandledCode(self):
        return self._isHandledCode

    @isHandledCode.setter
    def isHandledCode(self, code):
        self._isHandledCode = code


class YellowChatUser(YellowMessagesCarrierMixin):

    def __init__(self, userId, userHandler, maxMessages=MAX_STORED_MESSAGES_PER_USER):
        self._userId = userId
        self._userHandler = userHandler
        self._extendedProperties = {}
        super().__init__(maxMessages=maxMessages)

    @property
    def id(self):
        return self._userId

    @property
    def userHandler(self):
        return self._userHandler

    @property
    def extendedProperties(self):
        return self._extendedProperties

    def updateExtendedProperty(self, key, value):
        self._extendedProperties[key] = value


class YellowChat(YellowUsersCarrierMixin, YellowMessagesCarrierMixin):

    def __init__(self, chatId, maxMessages=MAX_STORED_MESSAGES_PER_CHAT):
        super().__init__(maxMessages=maxMessages)
        self._id = chatId

    @property
    def id(self):
        return self._id


class __YellowChatBotSuperclass(YellowUsersCarrierMixin, YellowMessagesCarrierMixin):
    """this is an abstract class"""

    def __init__(self, maxMessages=MAX_STORED_MESSAGES_PER_BOT):
        super().__init__(maxMessages=maxMessages)
        self._chats = {}

    @property
    def chats(self):
        return self._chats

    def addChat(self, chat):
        self._chats[chat.id] = chat

    def getChat(self, chatId):
        if chatId in self._chats:
            return self._chats[chatId]
        else:
            return None

    def getUpdates(self):
        pass

    def sendMessage(self, chat, message):
        pass


class YellowTelegram(__YellowChatBotSuperclass):

    baseUrl = "https://api.telegram.org/bot"
    _getUpdatesAPIMethod = "getUpdates"
    _sendMessageAPIMethod = "sendMessage"

    headers = {"content-type": "application/json"}
    messageLengthLimit = 4000

    def __init__(
        self,
        telegramKey=environment.telegramKey,
        maxMessages=MAX_STORED_MESSAGES_PER_BOT,
    ):
        super().__init__(maxMessages=maxMessages)
        self._rootUrl = "{}{}/".format(self.baseUrl, telegramKey)
        self._offset = 0

    def _pollForUpdates(self, offset=0):
        url = "{}{}".format(self._rootUrl, self._getUpdatesAPIMethod)
        data = {"offset": offset, "allowed_updates": "message"}

        result = requests.post(url, data=data)

        return result.json()

    def getUpdates(self):
        """
        {
            'ok': True,
            'result': [{
                'update_id': 3347538,
                'message': {
                    'message_id': 285,
                    'from': {
                        'id': 1********,
                        'is_bot': False,
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'username': 'jd',
                        'language_code': 'en'
                    },
                    'chat': {
                        'id': 1********,
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'username': 'jd',
                        'type': 'private'
                    },
                    'date': 1711836319,
                    'text': 'test'
                }
            }]
        }
        """

        updates = self._pollForUpdates(self._offset)

        if "result" in updates:
            result = updates["result"]
        else:
            updates = {"ok": False}
            result = ""

        if updates["ok"] and len(result) > 0:
            for update in result:
                self._offset = update["update_id"] + 1
                chatId = update["message"]["chat"]["id"]
                messageId = update["message"]["message_id"]
                messageText = update["message"]["text"]
                messageDate = update["message"]["date"]
                userId = update["message"]["from"]["id"]
                userHandler = update["message"]["from"]["username"]
                userFirstName = update["message"]["from"]["first_name"]
                userLastName = update["message"]["from"]["last_name"]

                chat = self.getChat(chatId)
                if chat is None:
                    chat = YellowChat(chatId)
                    self.addChat(chat)

                user = self.getUser(userId)
                if user is None:
                    user = YellowChatUser(userId, userHandler)
                    user.updateExtendedProperty("firstName", userFirstName)
                    user.updateExtendedProperty("lastName", userLastName)
                    self.addUser(user)

                message = YellowChatMessage(messageId, messageDate, messageText)
                message.chatId = chat.id
                message.userId = user.id

                self.addMessage(message)
                user.addMessage(message)
                chat.addMessage(message)
                chat.addUser(user)

        return updates

    def sendMessage(self, chat, message):
        url = "{}{}".format(self._rootUrl, self._sendMessageAPIMethod)
        messageParts = []
        msgLength = len(message)
        print(msgLength)
        print("---")
        ptr = 0
        while ptr < msgLength:
            step = ptr + self.messageLengthLimit
            cut = step if step < msgLength else msgLength
            messageParts.append(message[ptr:cut]) 
            ptr = step
            print(ptr)

        for messagePart in messageParts:
            data = {"chat_id": chat, "text": messagePart}
            result = requests.post(url, data=data)

        return result.json()
