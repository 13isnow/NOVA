import os 
from datetime import datetime

class Logger:
    def __init__(self):
        dir = os.path.join(os.getcwd(), "Logs")
        if not os.path.exists(dir):
            os.mkdir(dir)
        current_time = datetime.now()
        self.path = os.path.join(dir, f"{current_time.strftime("%Y-%m-%d-%H-%M-%S")}-log.txt")
        self.logfile = []

    def log(self, message):
        self.logfile.append(message)

    def logend(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            for line in self.logfile:
                f.write(line + '\n')
    
    def logsep(self, sep="#"):
        self.logfile.append(sep * 30)