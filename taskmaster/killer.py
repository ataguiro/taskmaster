import os
import signal
import time

from taskmaster.task_signal import *
from taskmaster.debug import *

import taskmaster.settings as settings

def getSignal(stopsignal):
    signals = ["TERM", signal.SIGTERM, "HUP", signal.SIGHUP, "INT", signal.SIGINT, \
        "QUIT", signal.SIGQUIT, "KILL", signal.SIGKILL, "USR1", signal.SIGUSR1, \
        "USR2", signal.SIGUSR2] 

    a = 0
    for i in signals:
        
        if a == 1:
            return int(i)
        if stopsignal == i:
            a = 1

def killer(pid, null):

    if pid == "Not Started":
        return 1
    name = settings.pid2name[pid]
    if settings.tab_process[name].status != "STARTING" and settings.tab_process[name].status != "RUNNING" \
        and settings.tab_process[name].status != "BACKOFF":
        return 1
    if settings.tab_process[name].status == "STOPPING":
        settings.tab_process[name].status = "STOPPED"
    father = settings.tab_process[name].father
    custom_signal = getSignal(settings.tab_prog[father].stopsignal)
    settings.tab_process[name].status = "STOPPING"
    try:
        os.kill(int(pid), custom_signal)
    except ProcessLookupError:
        return 1
    time.sleep(settings.tab_prog[father].stopwaitsecs)
    try:        
        if settings.tab_process[name].status != "STOPPED":
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    except KeyError:
        pass
