import os
import time

class log:
    def __init__(self):
        self.logfile = open("/tmp/logfile" + str(os.getpid()), "w+")
        self.logfile.write(str(os.getpid()))
        self.logfile.write("Session begins at :" + str(time.localtime()) + "\n")

    def update(self, event):
        self.logfile.write(str(os.getpid()))
        self.logfile.write(event)
