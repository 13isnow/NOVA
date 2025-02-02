import random
import json
import re

from LLMAgent import LLMAgent
from Memory import History
from Prompt import BasePrompt, CharacterPrompt, GameFlowPrompt

class Player:
    def __init__(self, num):
        self.num = num
        self.vaild = True
        self.card = None

    def getCard(self, card):
        self.card = card

    def isAlive(self):
        return self.vaild
    
    def die(self):
        self.vaild = False

    def think(self):
        pass

    def vote(self, choices):
        pass
    
    def speak(self):
        pass

    def memorize(self):
        pass

    def info(self):
        pass

class LLMPlayer(Player):
    def __init__(self, num):
        super().__init__(num)
        self.memory = History(lenlimit=20)
        self.memory.set(BasePrompt.RulePrompt)
        self.memory.set(f"你是Player {num}, 记住你的编号，不要让自己死亡")
        self.agent = LLMAgent()
        self.assistant = LLMAgent()

    def getCard(self, card):
        super().getCard(card)
        self.memory.set(CharacterPrompt.characters[card])

    def think(self, prompt):
        prompt = self.memory.get() + [{'role':'user', 'content': prompt}]
        return self.agent.chat(prompt)

    def vote(self, choices):
        prompt = self.memory.get() + [
            {'role':'user', 'content': GameFlowPrompt.VotePrompt}, 
            {'role':'system', 'content': f"请从{choices}中选择你要投票的对象，不要把票投给已经死亡的人"}
        ]
        words = self.agent.chat(prompt)
        try:
            choice = int(re.findall(r'\d+', words)[-1])
        except Exception as e:
            print(words)
            print(re.findall(r'\d+', words))
            raise e
        
        return choice
    
    def speak(self):
        prompt = self.memory.get() + [{'role':'user', 'content': GameFlowPrompt.DiscussionPrompt}]
        return self.agent.chat(prompt)
    
    def memorize(self, messages, set_memory=False):
        if set_memory:
            for message in messages:
                self.memory.set(message)
        else:
            for message in messages:
                self.memory.add(message)

    def reflect(self):
        memory = self.memory.get()
        message = self.assistant.chat(memory)
        self.memory.add(message, do_memory=True)

    def info(self):
        return self.memory.get()

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
RESET = "\033[0m"

class HumanPlayer(Player):
    def __init__(self, num):
        super().__init__(num)
        print(BLUE + f'你是Player {num}, 记住你的编号' + RESET)

    def getCard(self, card):
        super().getCard(card)
        print(BLUE + f'你是的身份是{card}, 请不要暴露' + RESET)

    def think(self, *args, **kwargs):
        return input(BLUE + "What do you think?\t" + RESET)

    def vote(self, choices, *args, **kwargs):
        while True:
            choice = int(re.findall(r'\d+', input(BLUE + f"What do you vote from {choices}?\t" + RESET))[0])
            if choice in choices:
                return choice
            else:
                print(type(choice))
                print(f"Invalid choice {choice}")

    def speak(self, *args, **kwargs):
        return input(BLUE + "What do you want to say?\t" + RESET)
    
    def memorize(self, *args, **kwargs):
        pass

    def info(self):
        pass

    