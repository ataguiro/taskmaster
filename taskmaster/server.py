import sys
import time
import socket
import threading
import configparser 
import os
import signal

from taskmaster.debug import *
from taskmaster.task_signal import *
from taskmaster.drop_root import *
from taskmaster.task_error import *
from taskmaster.extract import *
from taskmaster.manager import manager
from taskmaster.keeper import keeper
from taskmaster.watcher import watcher
from taskmaster.serviter import serviter, logging
from taskmaster.killer import killer
from taskmaster.dispatcher import dispatcher
from taskmaster.protect import *

class Server:
    def __init__(self, path):
        self.config = configparser.ConfigParser()
        try:
            self.config.read(path)
        except configparser.DuplicateSectionError:
            error_msg("Duplicate section on config file")
        try:
            self.psswd = self.config.get('server', 'password')
        except:
            self.psswd = None
        try:
            self.port = int(self.config.get('server', 'port'))
        except configparser.NoSectionError:
            error_msg("No field server - port")
        except configparser.DuplicateSectionError: 
            error_msg("Duplicate section on server")
        drop_privileges()
        self.pid = os.getpid()
        self.host = ''
        self.ss = socket.socket()
        self.c = None
        self.addr = None
        try:
            self.ss.bind((self.host, self.port))
        except:
            error_msg("Socket already in use")
        self.ss.listen(5)
        self.list_progs = extractProg(self.config.sections())
        if protect_stackoverflow(self.list_progs, self.config):
            error_msg("taskmasterd: Too much process asked, risk of stackoverflow, submit another config")
        signal.signal(signal.SIGCHLD, check_exit) 


    def start_manager(self, config, list_progs, old_list_progs):
       t = threading.Thread(target=manager, args=(config, list_progs, self, old_list_progs))
       t.start()
    
    def start_keeper(self):
        t = threading.Thread(target=keeper)
        t.start()

    def start_serviter(self):
        t = threading.Thread(target=serviter, args=(self.c, self.addr, self))
        t.start()

    def start_killer(self, pid):
        t = threading.Thread(target=killer, args=(pid, None))
        t.start()

    def start_dispatcher(self):
        t = threading.Thread(target=dispatcher)
        t.start()
