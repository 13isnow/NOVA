from LLMAgent import LLMAgent
from Prompt import AssistantPrompt

class Commenter:
    def __init__(self):
        self.assistant = LLMAgent()
    
    def comment(self, log):
        return self.agent.chat([AssistantPrompt.ConclusionPrompt.format(background=log)])
       