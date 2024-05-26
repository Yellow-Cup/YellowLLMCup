"""
The expected output of an agent is a dictionary of the following kind:
{ "role":None, 
  "response": str->...
}
"""

def lockRoleInChatAgent(*args, yellowLLMCupInstance, message, **kwargs):
    return yellowLLMCupInstance.lockRoleInChat(message=message)

def unlockRoleInChatAgent(*args, yellowLLMCupInstance, message, **kwargs):
    return yellowLLMCupInstance.unlockRoleInChat(message=message)

def dropContextAgent(*args, yellowLLMCupInstance, message, **kwargs):
    return yellowLLMCupInstance.clearContext(message=message)

# def yellowLLMLockRoleAgent(yellowLLMClientInstance, **kwargs):
#     yellowLLMClientInstance.isRoleLocked = True
#     return {
#         "role": None,
#         "response": "The role is locked: {}".format(yellowLLMClientInstance.role)
#     }

# def yellowLLMUnlockRoleAgent(yellowLLMClientInstance, **kwargs):
#     yellowLLMClientInstance.isRoleLocked = False
#     return {
#         "role": None,
#         "response": "The role is unlocked"
#     }

agents = {  # don't add "dialogue" agent, this one is added in yellowLLMClient package
    "lockRole": {
        "description": "the instructs you to stick to the current role and prevent it from changing. The input might be single 'lock' word or a more long imperative",
        "method": lockRoleInChatAgent  # yellowLLMLockRoleAgent
    },
    "unlockRole": {
        "description": "the user instructs you to unlock role changing and be able to switch roles dynamically. The input might be single 'unlock' word or a more long imperative",
        "method": unlockRoleInChatAgent  # yellowLLMUnlockRoleAgent
    },
    "clearContext": {
        "description": "the user instructs you to clear current discussion context. The input has to contain imperative,like 'drop context', 'clear context' or a another imperative of similar meaning",
        "method": dropContextAgent 
    },
}
