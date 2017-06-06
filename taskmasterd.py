import sys
import signal
import time
import socket
import configparser
import threading
import logging

import taskmaster.settings as settings

from taskmaster.daemonize import *
from taskmaster.server import *
from taskmaster.debug import *
from taskmaster.task_error import *
from taskmaster.serviter import num_threads

if  __name__ == '__main__':
    DG_init(0)
    settings.init()
    if len(sys.argv) < 2:
        error_msg("usage : <config_file>")
    if len(sys.argv) > 2 and sys.argv[2] == "-m":
        settings.opt = 1
    else:
        settings.opt = 0
    try:
        path_config = os.path.abspath(sys.argv[1])
    except FileNotFoundError:
        error_msg("No such configuration file")
    daemonize()
    logging.basicConfig(format='%(asctime)s , %(levelname)s : %(message)s', \
        filename='/tmp/.taskmasterdlog', level=logging.INFO)
    server = Server(path_config)
    server.start_keeper()
    server.start_dispatcher()
    logging.info("Taskmasterd server started")
    server.start_manager(server.config, server.list_progs, None)

    try:
        while True:
            global num_threads
            server.c, server.addr = server.ss.accept()
            logging.info("Connection client %s from %s", server.addr[1], server.addr[0])
            server.c.recv(1024)
            server.c.send(str(num_threads).encode('utf-7'))
            server.start_serviter()
            num_threads += 1
        server.ss.close()
    except InterruptedError:
        error_msg("Interrupted syscall") 
