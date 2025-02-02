import json
import random

from Prompt import GameFlowPrompt

class WereWolfRules:
    def __init__(self):
        pass

    @staticmethod
    def get(rule, *args):
        if rule == 'win':
            return GameRules()
        if rule == 'deal':
            return DealRules(*args)
        if rule == 'wolf':
            return WolfRules()
        if rule == 'priest':
            return PriestRules()
        if rule == 'vote':
            return VoteRules()
        return None

class GameRules:
    def __init__(self):
        pass

    @staticmethod
    def check(wolf_num, priesthood_num, villager_num):
        if wolf_num >= villager_num:
            return True, 'wolf'
        if wolf_num == 0:
            return True, 'villager'
        
        return False, None

class DealRules:
    def __init__(self, player_num):
        self.deal_list = []
        with open('char-config.json', 'r') as f:
            config = json.load(f)
            char_config = config[str(player_num)]
            for char, num in char_config.items():
                self.deal_list += [char] * num

        random.shuffle(self.deal_list)

    def deal(self):
        return self.deal_list.pop()

class WolfRules:
    def __init__(self):
        pass
    
    def kill(self, wolves, vaildplayers):
        votes = []
        discussion = []
        for wolf in wolves:
            discussion.append(f'Wolf {wolf.num}:' + wolf.think(GameFlowPrompt.WolfKillPrompt + f"现阶段剩余的人有{vaildplayers}"))

        for wolf in wolves:
            wolf.memorize(discussion)

        for wolf in wolves:
            votes.append(wolf.vote(vaildplayers))

        return votes

class PriestRules:
    def __init__(self):
        pass
    def act(self, prompt):
        pass

class VoteRules:
    def __init__(self):
        pass
    def judge(self, votes):
        return max(set(votes), key=votes.count)