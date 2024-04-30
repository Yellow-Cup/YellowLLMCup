def yellowGPTLockRoleAgent(YellowGPTClientInstance, **kwargs):
    YellowGPTClientInstance.isRoleLocked = True
    return "The role is locked: {}".format(YellowGPTClientInstance.role)

def yellowGPTUnlockRoleAgent(YellowGPTClientInstance, **kwargs):
    YellowGPTClientInstance.isRoleLocked = False
    return "The role is unlocked"

agents = {  # don't add "dialogue" agent, this one is added in yellowGPTClient package
    "lockRole": {
        "description": "user wants system to stick to the current role and prevent it from changig. The input might be single 'lock' word or a more long imperative",
        "method": yellowGPTLockRoleAgent
    },
    "unlockRole": {
        "description": "user wants system to unlock role changing and be able to switch roles. The input might be single 'unlock' word or a more long imperative",
        "method": yellowGPTUnlockRoleAgent
    },
}
