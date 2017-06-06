import logging

import taskmaster.settings as settings

from taskmaster.launcher import *
from taskmaster.debug import *
from taskmaster.execute import *

def manager(config, list_progs, server, old_list_progs):

    if old_list_progs:
        for name in old_list_progs:
            if name not in list_progs:
                for process in settings.tab_process:
                    if settings.tab_process[process].father == name:
                        server.start_killer(settings.tab_process[process].pid)


    for name_prog in list_progs: 

        if name_prog in settings.tab_prog:
            new_prog = Program(config, name_prog)
            old_prog = settings.tab_prog[name_prog]
            numprocs = settings.tab_prog[name_prog].numprocs
            if new_prog.stdout != old_prog.stdout or new_prog.stderr != old_prog.stderr \
                or new_prog.env != old_prog.env or old_prog.env == None or new_prog.dir != old_prog.dir \
                or old_prog.dir == None or old_prog.umask == None \
                or new_prog.umask != old_prog.umask or new_prog.command != old_prog.command:
                settings.tab_prog.pop(name_prog, None)
                settings.tab_prog[name_prog] = new_prog

                for name in settings.tab_process:

                    if settings.tab_process[name].father == name_prog:
                        server.start_killer(settings.tab_process[name].pid)

                if new_prog.autostart == "true":

                    while numprocs > 0:
                        if settings.tab_prog[name_prog].numprocs > 1:
                            name_process = name_prog[8:] + "_" + str(numprocs)
                        else:
                            name_process = name_prog[8:]
                        logging.info("Start %s", name_process)
                        start_protected_launcher(settings.tab_prog[name_prog], name_process, name_prog, \
                            copy.copy(settings.tab_prog[name_prog].startretries))
                        numprocs -= 1

            else:

                if numprocs < new_prog.numprocs:
                    gap_num = numprocs
            
                    while gap_num != new_prog.numprocs:
                        name_process = name_prog[8:] + "_" + str(gap_num)
                        logging.info("Start %s", name_process)
                        launcher(settings.tab_prog[name_prog], name_process, name_prog, \
                            copy.copy(settings.tab_prog[name_prog].startretries))
                        gap_num += 1

                if new_prog.autorestart != old_prog.autorestart or new_prog.exitcodes != old_prog.exitcodes \
                    or new_prog.startsecs != old_prog.startsecs or new_prog.startretries != old_prog.startretries \
                    or new_prog.stopsignal != old_prog.stopsignal or new_prog.stopwaitsecs != old_prog.stopwaitsecs \
                    or new_prog.numprocs != old_prog.numprocs:

                    settings.tab_prog.pop(name_prog, None) 
                    settings.tab_prog[name_prog] = new_prog
 
        else:

            settings.tab_prog[name_prog] = Program(config, name_prog)
            numprocs = settings.tab_prog[name_prog].numprocs
            launch_num = 0

            if settings.tab_prog[name_prog].autostart == "true" \
                and settings.tab_prog[name_prog].command:

                while launch_num != numprocs:
                    if numprocs > 1:
                        name_process = name_prog[8:] + "_" + str(launch_num)
                    else:
                        name_process = name_prog[8:]
                    logging.info("Start %s", name_process)
                    launcher(settings.tab_prog[name_prog], name_process, name_prog, \
                        copy.copy(settings.tab_prog[name_prog].startretries))
                    launch_num += 1


            elif settings.tab_prog[name_prog].autostart == "false" \
                and settings.tab_prog[name_prog].command:
                
                while launch_num != numprocs:
                    if numprocs > 1:
                        name_process = name_prog[8:] + "_" + str(launch_num)
                    else:
                        name_process = name_prog[8:]
                    process = Process(name_process, "Not Started", "STOPPED", \
                        settings.tab_prog[name_prog].startretries, name_prog, -1, -1, -1)
                    settings.tab_process[name_process] = process
                    launch_num += 1
