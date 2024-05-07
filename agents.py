"""
The expected output of an agent is a dictionary of the following kind:
{ "role":None, 
  "response": str->...
}
"""

def lockRoleInChatAgent(*args, yellowLLMCupInstance, chatId, **kwargs):
    return yellowLLMCupInstance.lockRoleInChat(chatId=chatId)

def unlockRoleInChatAgent(*args, yellowLLMCupInstance, chatId, **kwargs):
    return yellowLLMCupInstance.unlockRoleInChat(chatId=chatId)

def yellowLLMLockRoleAgent(yellowLLMClientInstance, **kwargs):
    yellowLLMClientInstance.isRoleLocked = True
    return {
        "role": None,
        "response": "The role is locked: {}".format(yellowLLMClientInstance.role)
    }

def yellowLLMUnlockRoleAgent(yellowLLMClientInstance, **kwargs):
    yellowLLMClientInstance.isRoleLocked = False
    return {
        "role": None,
        "response": "The role is unlocked"
    }

agents = {  # don't add "dialogue" agent, this one is added in yellowLLMClient package
    "lockRole": {
        "description": "user wants system to stick to the current role and prevent it from changing. The input might be single 'lock' word or a more long imperative",
        "method": lockRoleInChatAgent  # yellowLLMLockRoleAgent
    },
    "unlockRole": {
        "description": "user wants system to unlock role changing and be able to switch roles dynamically. The input might be single 'unlock' word or a more long imperative",
        "method": unlockRoleInChatAgent  # yellowLLMUnlockRoleAgent
    },
}
