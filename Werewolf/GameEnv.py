import json

from Record import Logger
from Player import LLMPlayer, HumanPlayer
from Rules import WereWolfRules
from Memory import History

class Env:
    def __init__(self):
        self.day = 0

        self.player_num = 0
        self.players = []

        self.wolf_num = 0
        self.wolves = []

        self.priesthood_num = 0
        self.priesthoods = []

        self.villager_num = 0

        self.over = False
        self.winner = None

        self.GameRules = WereWolfRules.get('win')

    def reset(self, wolves, priesthoods, players):
        self.day = 1
        self.player_num = len(players)
        self.players = players
        self.wolf_num = len(wolves)
        self.wolves = wolves
        self.priesthood_num = len(priesthoods)
        self.priesthoods = priesthoods
        self.villager_num = self.player_num - self.wolf_num - self.priesthood_num
        self.over, self.winner = self.checkGameover()

    def checkGameover(self):
        return self.GameRules.check(self.wolf_num, self.priesthood_num, self.villager_num)
    
    def update(self, victim):
        self.day += 1
        victim.die()

        if victim in self.wolves:
            self.wolf_num -= 1
        elif victim in self.priesthoods:
            self.priesthood_num -= 1
        else:
            self.villager_num -= 1
        
        self.over, self.winner = self.checkGameover()

    def validPlayers(self):
        return [player.num for player in self.players if player.isAlive()]
    
    def GameOver(self):
        return self.over, self.winner
    


class WereWolfGame:
    def __init__(self):        
        self.env = Env()
        self.state = None
        self.logger = Logger()

        self.WolfKill = WereWolfRules.get('wolf')
        self.PriestAction = WereWolfRules.get('priest')
        self.VoteJudge = WereWolfRules.get('vote')

    def prepare(self, player_num=5, isPlayer=False):
        self.logger.log("Game Start")
        self.logger.log(f"Player Number: {player_num}")
        self.logger.logsep()

        roles = WereWolfRules.get('deal', player_num)

        players = []
        wolves = []
        priesthoods = []

        for num in range(player_num):
            if isPlayer:
                player = HumanPlayer(num)
                isPlayer = False
            else:
                player = LLMPlayer(num)

            role = roles.deal()
            player.getCard(role)
            players.append(player)

            if role == "wolf":
                wolves.append(player)
            elif role != "villager":
                priesthoods.append(player)

            self.logger.log(f"Player {player.num} get {player.card}")

        self.env.reset(wolves=wolves, priesthoods=priesthoods, players=players)
        self.logger.logsep()

    def updateState(self, victim):
        self.env.update(victim)

    def infoState(self):
        # print(json.dumps(self.state, ensure_ascii=False, indent=8))
        pass

    def info(self, message):
        self.logger.log(message)
        print(message)

    def infosep(self, sep='#'):
        self.logger.logsep(sep)
        print(sep * 30)
        
    def NightRound(self):
        print("Wolves, Open Your Eyes")
        votes = self.WolfKill.kill(self.wolves, self.vaildplayers)
        victim = self.players[self.VoteJudge.judge(votes)]
        self.info(f"Wolf kill Player {victim.num}")
        for player in self.players:
            player.memorize([f"Wolf kill Player {victim.num}"])
        self.updateState(victim)
        print("Wolves, Close Your Eyes")

        # print("Priest, Open Your Eyes") 
        # self.PriestAction.act(self.priesthoods)

    def DiscussionRound(self):
        print("Discussion Start")
        discussion = []
        for player in self.players:
            if player.isAlive():
                message = player.speak()
                discussion.append(f"Player {player.num}: {message}")
                self.info(f"Player {player.num}: {message}")
                self.infosep('-')
        for player in self.players:
            player.memorize(discussion)

    def VoteRound(self):
        print("Vote Start")
        votes = []
        for player in self.players:
            if player.isAlive():
                player_num = player.vote(self.vaildplayers)
                self.info(f"Player {player.num} vote Player {player_num}")
                votes.append(player_num)

        victim = self.players[self.VoteJudge.judge(votes)]
        self.info(f"Player {victim.num} is voted out")
        self.updateState(victim)

    def run(self):
        for player in self.players:
            player.memorize([f"游戏开始，共有{len(self.players)}名玩家, 玩家编号分别是{list(range(len(self.players)))}，请大家隐藏好身份，实现角色目标，取得胜利"], set_memory=True)
            
        while not self.gameover:
            self.infoState()
            self.info(f"Day {self.day}")
            print("Night Start, Close Your Eyes")
            self.NightRound()
            self.infosep('=')
            print("Day Start, Open Your Eyes")
            self.DiscussionRound()
            self.infosep('=')
            self.VoteRound()
            self.infosep('#')
        
        self.info(f"Game Over, Winner is {self.gameWinner}")
        self.logger.logend()

    @property
    def day(self):
        return self.env.day

    @property
    def vaildplayers(self):
        return self.env.validPlayers()
    
    @property
    def gameover(self):
        return self.env.over
    
    @property
    def gameWinner(self):
        return self.env.winner
    
    @property
    def players(self):
        return self.env.players
    
    @property
    def wolves(self):
        return self.env.wolves
    
    @property
    def priesthoods(self):
        return self.env.priesthoods
    
    @property
    def players(self):
        return self.env.players
    
    @property
    def vaildplayers(self):
        return self.env.validPlayers()