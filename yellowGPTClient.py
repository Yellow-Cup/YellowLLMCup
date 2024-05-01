import environment
from openai import OpenAI
from roles import roles
from agents import agents


defaultModel = "gpt-3.5-turbo"


roleDefinitionPrompt = """You have the following roles: {}; 
Tell which of these roles would respond to the user request better?
Return just role.
""".format(
    ", ".join(roles.keys())
)

agentsListing = ""

agents["dialogue"] = {
    "description": "default agent, poviding a regular chat response. Used when no other agents determined as best suitable for user's request.",
    "method": None
}

for agent in agents:
    agentsListing += "{}: {},\n ".format(agent, agents[agent]["description"])

agentDefinitionPrompt = str("""The agents list is provided in format 'name: description' and is the following: \n {} \n  
 Tell which of these agents would serve the user request better?
Return just agent name.
""".format(
    agentsListing[:-2]
))


class YellowGPTClient:
    """
    'defineAgent' defines agent and calls the corresponding method. If agent is 'dialogue', it calls 'defineRole'
    'defineRole' defines role, sets it to the instance, and calls 'query' to generate response.
    'query' generates a response from the perspective of a role set ('_role')
    """

    def __init__(
        self,
        defaultRole="Any",
        defaultAgent="dialogue",
        locked=False,
        model=defaultModel,
        openAI_API_Key=environment.openaiKey,
    ):
        global roles, agents

        self._client = OpenAI(api_key=openAI_API_Key)
        self._model = model

        self._roles = roles
        self._agents = agents
        self._agents["dialogue"]["method"] = self.defineRole

        self._isRoleLocked = locked
        self._role = defaultRole
        self._agent = defaultAgent

    @property
    def isRoleLocked(self):
        return self._isRoleLocked
    
    @isRoleLocked.setter
    def isRoleLocked(self, value):
        if isinstance(value, bool):
            self._isRoleLocked = value
        else:
            self._isRoleLocked = False

    @property
    def role(self):
        return self._role

    def query(self, message, systemMessage=None, context=None, showRole=True):
        if systemMessage is None:
            systemMessage = {"role": "system", "content": self._roles[self._role]}

        if context is not None:
            systemMessage[
                "content"
            ] += "\n Respond considering the context of the following discussion: {} \n".format(context)

        userMessage = {"role": "user", "content": message}

        aiResponse = self._client.chat.completions.create(
            model=self._model, messages=[systemMessage, userMessage]
        )

        response = aiResponse.choices[0].message.content
        if showRole:
            response = "Role: {}\n\n{}".format(self._role, response)

        return response

    def defineRole(self, *args, message, **kwargs):
        global roleDefinitionPrompt

        systemMessage = {"role": "system", "content": roleDefinitionPrompt}
        
        if not self.isRoleLocked:
            role = self.query(message=message, systemMessage=systemMessage, showRole=False)

            if role in self._roles:
                self._role = role

        return self.query(message=message, **kwargs)

    def defineAgent(self, message, **kwargs):
        global agentDefinitionPrompt

        systemMessage = {"role": "system", "content": agentDefinitionPrompt}

        agent = self.query(message=message, systemMessage=systemMessage, showRole=False)

        if agent in self._agents:
            self._agent = agent

        return self._agents[self._agent]["method"](self, message=message, **kwargs)
