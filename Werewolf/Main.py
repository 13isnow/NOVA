from GameEnv import WereWolfGame

if __name__ == '__main__':
    game = WereWolfGame()
    game.prepare(5, isPlayer=True)
    game.run()