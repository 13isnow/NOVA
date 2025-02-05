import re

import asyncio
import concurrent.futures
from ollama import Client

class LLMAgent:
    def __init__(self):
        self.agent = Client()
        self.model = "deepseek-r1"
        self.prompt = []

    def set(self, prompt):
        self.prompt.append({"role": "system", "content": prompt})

    def chat(self, messages: list):
        messages = self.prompt + messages
        response = self.agent.chat(model=self.model, messages=messages)
        return re.sub(r'<think>.*?</think>', '', response["message"]["content"], flags=re.DOTALL)


if __name__ == "__main__":
    agent = LLMAgent()
    prompt = "现在假装你是一名南京大学（NJU）的学生，请不要暴露自己是AI或者非人类的生物，回答我的问题"
    agent.set(prompt)
    message = "你好，请介绍一下你自己?"
    print(agent.chat([{"role": "user", "content": message}]))