import logging

from taskmaster.debug import *
from taskmaster.launcher import * 
from taskmaster.task_signal import *
from taskmaster.watcher import *
from taskmaster.report import *

import taskmaster.settings as settings

def clean_fd(name):

    infd = settings.tab_process[name].process_fd[0]
    outfd = settings.tab_process[name].process_fd[1]
    errfd = settings.tab_process[name].process_fd[2]
    os.close(infd)
    settings.queue_old_fd.append(outfd)
    settings.queue_old_fd.append(errfd)

def guardian(pid, null):

    for process in settings.tab_process:
        if pid == settings.tab_process[process].pid:
            settings.tab_process[process].status = "UNKNOWN"
            name = settings.pid2name[pid]
            logging.info("Process %s in UNKOWN", name)

def keeper():

    while 1 :
        while len(settings.queue_pid) > 1:
            pid = settings.queue_pid[0]
            try:
                name = settings.pid2name[pid]
                exitcode = settings.queue_pid[1]
                name_prog = settings.tab_process[name].father
                program = settings.tab_prog[name_prog]
                watcher(name)
                watcher_backoff(name)
                clean_fd(name)
                if exitcode not in program.exitcodes:
                    reporter(name_prog, None)  
                if ((str(exitcode) not in program.exitcodes and program.autorestart == "unexpected") \
                    or (program.autorestart == "true")) and settings.tab_process[name].status == "RUNNING":
                    logging.info("Autorestart %s with status %s", name, program.autorestart)
                    launcher(program, name, name_prog, program.startretries)
                elif settings.tab_process[name].status == "RUNNING":
                    settings.tab_process[name].status = "EXITED"
                elif settings.tab_process[name].status == "STOPPING":
                    settings.tab_process[name].status = "STOPPED"
                elif settings.tab_process[name].status == "BACKOFF":
                    if settings.tab_process[name].retries > 0:
                        settings.tab_process[name].retries -= 1 
                        logging.info("Start %s from backoff", name)
                        launcher(program, name, name_prog, settings.tab_process[name].retries)
                    elif settings.tab_process[name].retries == 0:
                        start_reporter(name_prog)
                        logging.info("Process %s in FATAL", name)
                        settings.tab_process[name].status = "FATAL"
            except OSError:
                t = threading.Thread(target=guardian, args=(pid, None))
                t.start()
            except KeyError:
                pass
            settings.queue_pid.pop(0)
            settings.queue_pid.pop(0)
        time.sleep(1)
