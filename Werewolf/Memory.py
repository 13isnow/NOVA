from LLMAgent import LLMAgent

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
        pass

    def add(self, message, do_memory=False):
        self.shortHistory.append({"role": "user", "content": message})
        self.len += 1

        if self.len > self.lenlimit or do_memory:
            self.summarize()
            self.reset()

    def get(self):
        return self.longHistory + self.shortHistory

    


