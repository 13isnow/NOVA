from LLMAgent import LLMAgent
from Prompt import AssistantPrompt

class Commenter:
    def __init__(self):
        self.assistant = LLMAgent()
    
    def comment(self, log):
        return self.assistant.chat([{
            'role': 'user',
            'content': AssistantPrompt.ConclusionPrompt.format(background=log)
        }])
       