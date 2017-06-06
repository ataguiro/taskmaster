import taskmaster.settings as settings

from taskmaster.debug import *

def cleaner(list_progs):

    to_del = list()

    for name in settings.tab_process:

        if "program:" + name.split('_')[0] not in list_progs \
            and  (settings.tab_process[name].status == "STOPPED" or \
            settings.tab_process[name].status == "EXITED" or \
            settings.tab_process[name].status == "FATAL" or \
            settings.tab_process[name].status == "UNKNOWN"):
                to_del.append(name) 

    for name in to_del:
        settings.tab_process.pop(name, None)

    to_del = list()

    for name_prog in settings.tab_prog:

        num_process = 0
        for name_process in settings.tab_process:
            if settings.tab_process[name_process].father == name_prog:
                num_process += 1
        if num_process == 0:
            to_del.append(name_prog)

    for name in to_del:
        settings.tab_prog.pop(name, None)
