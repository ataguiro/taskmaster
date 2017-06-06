import configparser

import taskmaster.settings as settings

from taskmaster.debug import *
from taskmaster.watcher import *

def getStatus(list_progs):
    
    tab = list()
     
    max_padding = 0
    max_padding_pid = 0
    for name in settings.tab_process:
        if len(name) > max_padding:
            max_padding = len(name)
        if len(str(settings.tab_process[name].pid)) > max_padding_pid:
            max_padding_pid = len(str(settings.tab_process[name].pid))
    
    max_padding += 15
    max_padding_pid += 15

    for name in settings.tab_process:

        watcher(name)
        name_padding = max_padding - len(name)
        padone = " " * name_padding

        pid_padding = max_padding_pid - len(str(settings.tab_process[name].pid))
        padtwo = " " * pid_padding
            
        tab.append(name + padone + str(settings.tab_process[name].pid) + padtwo + \
            settings.tab_process[name].status + "\n") 
    
    return tab


def getConfig(config, name_prog):

    tab = list()

    try:
        tab.append("command: " + config.get(name_prog, "command"))
    except configparser.NoOptionError:
        tab.append("command: None")    
    try:
        tab.append("numprocs: " + config.get(name_prog, "numprocs"))
    except configparser.NoOptionError:
        tab.append("numprocs: 1")    
    try:
        tab.append("autostart: " + config.get(name_prog, "autostart"))
    except configparser.NoOptionError:
        tab.append("autostart: true")
    try:
        tab.append("autorestart: " + config.get(name_prog, "autorestart"))
    except configparser.NoOptionError:
        tab.append("autorestart: unexpected") 
    try:
        tab.append("exitcodes: " + config.get(name_prog, "exitcodes"))
    except configparser.NoOptionError:
        tab.append("exitcodes: 0")
    try:
        tab.append("startsecs: " + config.get(name_prog, "startsecs"))
    except configparser.NoOptionError:
        tab.append("startsecs: 1")
    try:
        tab.append("startretries: " + config.get(name_prog, "startretries"))
    except configparser.NoOptionError:
        tab.append("startretries: 3")
    try:
        tab.append("stopsignal: " + config.get(name_prog, "stopsignal"))
    except configparser.NoOptionError:
        tab.append("stopsignal: TERM")
    try:
        tab.append("stopwaitsecs: " + config.get(name_prog, "stopwaitsecs"))
    except configparser.NoOptionError:
        tab.append("stopwaitsecs: 10")
    try:
        tab.append("stdout_logfile: " + config.get(name_prog, "stdout_logfile"))
    except configparser.NoOptionError:
        tab.append("stdout_logfile: /dev/null")
    try:
        tab.append("stderr_logfile: " + config.get(name_prog, "stderr_logfile"))
    except configparser.NoOptionError:
        tab.append("stderr_logfile: dev/null")
    try: 
        tab.append("environnement: " + config.get(name_prog, "environnement"))
    except configparser.NoOptionError:
        pass
    try:
        tab.append("directory: " + config.get(name_prog, "directory"))
    except configparser.NoOptionError:
        pass
    try:
        tab.append("umask: " + config.get(name_prog, "umask"))
    except configparser.NoOptionError:
        pass

    return (tab)

def getAll(cmd):

    tab = list()
    tab.append(cmd)
    for name in settings.tab_process:
        tab.append(name)

    return (tab)
