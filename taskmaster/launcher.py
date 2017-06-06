import os
import sys 
import time
import copy
import pty
import logging
import threading

from taskmaster.debug import *
from taskmaster.task_error import *

import taskmaster.settings as settings

def start_launcher(program, name_process, name_prog, retries):
    t = threading.Thread(target=launcher, args=(program, name_process, name_prog, retries))
    t.start()

def start_protected_launcher(program, name_process, name_prog, retries):
    t = threading.Thread(target=protected_launcher, args=(program, name_process, name_prog, retries))
    t.start()

class Process:
    def __init__(self, name_process, pid, status, retries, name_prog, write_in, read_out, read_err):
        self.name_process = name_process
        self.pid = pid
        self.status = status
        self.retries = retries
        self.father = name_prog
        self.time = time.time()
        self.process_fd = [write_in, read_out, read_err]

def protected_launcher(program, name_process, name_prog, retries):
     
    try:
        while settings.tab_process[name_process].status != "EXITED" and settings.tab_process[name_process].status != "STOPPED" \
            and settings.tab_process[name_process].status != "FATAL" and settings.tab_process[name_process].status != "UNKNOWN":
            time.sleep(1)
    except KeyError:
        return
    launcher(program, name_process, name_prog, retries)

def launcher(program, name_process, name_prog, retries):

    read_in, write_in = os.pipe()
    read_out, write_out = os.pipe()
    read_err, write_err = os.pipe()

    try:
        pid = os.fork()
    except BlockingIOError:
        logging.info("Taskmasterd server ended")
        error_msg("Fork temporary unavailable, taskmasterd exiting")

    if pid > 0: 
        settings.fds.append(read_out)
        settings.fds.append(read_err)
        settings.fd2realfile[read_out] = program.stdout
        settings.fd2realfile[read_err] = program.stderr
        os.close(read_in)
        os.close(write_out)
        os.close(write_err)
        if program.startsecs > 0:
            status = "STARTING"
        elif program.startretries > retries:
            status = "BACKOFF"
        else:
            status = "RUNNING"
        process = Process(name_process, pid, status, retries, name_prog, write_in, read_out, read_err)
        settings.pid2name[pid] = name_process
        settings.tab_process[name_process] = process
        settings.lst_pid.append(pid)

    if pid == 0:
        os.dup2(read_in, 0)
        os.dup2(write_out, sys.stdout.fileno())
        os.dup2(write_err, sys.stderr.fileno())
        os.close(write_in)
        os.close(read_out)
        os.close(read_err)
        program.conf()
        try:
            args = program.command.split(' ')
            os.execv(args[0], args)
        except:
            sys.exit(-1)
