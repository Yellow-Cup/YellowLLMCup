import environment
from openai import OpenAI
import roles
from agents import agents


defaultModel = "gpt-3.5-turbo"
defaultAgent = "dialogue"

roleDefinitionPrompt = """You have the following roles: {}; 
Tell which of these roles would respond to the user request better?
Return just role.
""".format(
    ", ".join(roles.roles.keys())
)

agentsListing = ""

agents[defaultAgent] = {
    "description": "default agent, poviding a regular chat response. Used when no other agents determined as best suitable for user's request.",
    "method": None,
}

for agent in agents:
    agentsListing += "{}: {},\n ".format(agent, agents[agent]["description"])

agentDefinitionPrompt = str(
    """The agents list is provided in format 'name: description' and is the following: \n {} \n  
 Tell which of these agents would serve the user request better?
Return just agent name.
""".format(
        agentsListing[:-2]
    )
)


class YellowLLMClient:
    """
    'defineAgent' defines agent and calls the corresponding method. If agent is 'dialogue', it calls 'defineRole'
    'defineRole' defines role, sets it to the instance, and calls 'query' to generate response.
    'query' generates a response from the perspective of a role set ('_role')
    """

    def __init__(
        self,
        locked=False,
        model=defaultModel,
        openAI_API_Key=environment.openaiKey,
    ):

        self._client = OpenAI(api_key=openAI_API_Key)
        self._model = model

        self._roles = roles.roles
        self._agents = agents
        self._agents["dialogue"]["method"] = self.defineRole

        self._isRoleLocked = locked
        self._role = roles.defaultRole

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
    
    @role.setter
    def role(self, roleSuggestion):
        if roleSuggestion in self._roles:
            self._role = roleSuggestion
        else:
            self._role = roles.defaultRole

    def query(
        self, prompt, role=None, systemMessage=None, context=None, showRole=True, **kwargs
    ):
        if role is None:
            role = self.role

        if systemMessage is None:
            systemMessage = {"role": "system", "content": self._roles[role]["content"]}

        if context is not None:
            systemMessage[
                "content"
            ] += "\n Respond considering the context of the following discussion: {} \n".format(
                context
            )

        userMessage = {"role": "user", "content": prompt}

        aiResponse = self._client.chat.completions.create(
            model=self._model, messages=[systemMessage, userMessage]
        )

        response = aiResponse.choices[0].message.content
        if showRole:
            response = "{}:\n\n{}".format(role, response)

        return {"response": response, "role": role}

    def defineRole(self, *args, prompt, isRoleLocked=None, **kwargs):
        global roleDefinitionPrompt

        systemMessage = {"role": "system", "content": roleDefinitionPrompt}

        if isRoleLocked is None:
            isRoleLocked = self.isRoleLocked

        if not isRoleLocked:
            role = self.query(
                prompt=prompt, systemMessage=systemMessage, showRole=False
            )["response"]

            self.role = role

            kwargs["role"] = self.role

        return self.query(prompt=prompt, **kwargs)

    def defineAgent(self, prompt, **kwargs):
        global agentDefinitionPrompt, defaultAgent

        systemMessage = {"role": "system", "content": agentDefinitionPrompt}

        agent = self.query(
            prompt=prompt, systemMessage=systemMessage, showRole=False
        )["response"]

        if agent not in self._agents:
            agent = defaultAgent

        return self._agents[agent]["method"](self, prompt=prompt, **kwargs)
