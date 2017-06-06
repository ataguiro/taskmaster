import os
import inspect
import re
import random
import threading

BG_DEF="\033[49m"
BG_RED="\033[41m"
BG_GREEN="\033[42m"
BG_YELLOW="\033[43m"
BG_BLUE="\033[44m"
BG_MAGENTA="\033[45m"
BG_CYAN="\033[46m"

FG_WHITE="\033[97m"

pid_color = 0
fatherpid = 0

def DG_init(init):
    global pid_color
    global fatherpid
    
    fatherpid = os.getpid()
    dbg_colors = [BG_RED, BG_BLUE, BG_MAGENTA, BG_YELLOW]
    pid_color = random.choice(dbg_colors)
    if init == 0:
        print(BG_GREEN + "START", file=open("/tmp/STDBUG", "a+"), flush=True)

def DG(message):

    if os.getpid() != fatherpid:
        DG_init(1)
    stdbug = open("/tmp/STDBUG", "a+")
    frame = inspect.stack()[1]
    info =  inspect.getframeinfo(frame[0])
    list_path = re.split('/', info.filename)
    filename = list_path[len(list_path) - 1]
    pid = str(os.getpid())
    thread = str(threading.get_ident())[12:]
    align = 40 - (len(pid) + len(filename) + len(thread))
    space = str()
    while align > 0:
        space += ' '
        align -= 1
    print(pid_color + FG_WHITE + pid, thread, filename, space,
        ":" + BG_DEF + "  " + message, file=open("/tmp/STDBUG", "a+"), flush=True)

def show_tab_process(tab_process):

    DG("BEGIN SHOW")
    for name in  tab_process:
        DG("data for " + name)
        DG("name is : " +  tab_process[name].name_process)
        DG("pid is : " +  tab_process[name].status)
        DG("status is : " +  str(tab_process[name].pid))

    DG("END SHOW")

