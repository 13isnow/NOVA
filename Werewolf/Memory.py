from LLMAgent import LLMAgent
from Prompt import AssistantPrompt

class History:
    def __init__(self, lenlimit=20):
        self.len = 0
        self.lenlimit = lenlimit
        self.assistant = LLMAgent()
        self.longHistory = []
        self.shortHistory = []

    def set(self, memory):
        self.longHistory.append({"role": "system", "content": memory})

    def reset(self):
        self.shortHistory = []
        self.len = 0

    def summarize(self):
        history = '##\n\n##'.join([item['content'] for item in self.shortHistory])
        prompt = [{"role": "system", "content": AssistantPrompt.SummaryPrompt + history}]
        response = self.assistant.chat(prompt)
        self.longHistory.append({"role": "system", "content": response})
        
    def add(self, message, do_summarize=False):
        self.shortHistory.append({"role": "user", "content": message})
        self.len += 1

        if self.len > self.lenlimit or do_summarize:
            self.summarize()
            self.reset()

    def get(self):
        return self.longHistory + self.shortHistory

    


