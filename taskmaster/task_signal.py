import signal

import taskmaster.settings as settings

from taskmaster.debug import *

def check_exit(number, frame):

    while True:
        try:
            pid = os.waitpid(0, 0)
            settings.queue_pid += pid;
        except:
            break
