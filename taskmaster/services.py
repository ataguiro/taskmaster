import socket
import configparser 
import logging
import signal
import tty

import taskmaster.settings as settings

from taskmaster.debug import * 
from taskmaster.execute import *
from taskmaster.task_error import *
from taskmaster.statutor import *
from taskmaster.report import reporter, manual_reporter
from taskmaster.extract import *
from taskmaster.keeper import *
from taskmaster.cleaner import cleaner
from taskmaster.ioprocess import *
from taskmaster.protect import *

def services(clientsocket, addr, server):

    while True:
        m = clientsocket.recv(1024)
        dec = m.decode("utf-8")
        cmd_lst = dec.split(' ')
        try:
            if cmd_lst[1] == "all":
                cleaner(server.list_progs)
                cmd_lst = getAll(cmd_lst[0])
        except IndexError:
            pass
        
        if cmd_lst[0] == 'exit' or cmd_lst[0] == 'quit' or not m:
            break

        elif cmd_lst[0] == 'start':
            for cmd in cmd_lst[1:]:
                try:
                    if settings.tab_process[cmd].status != "RUNNING" and settings.tab_process[cmd].status != "STARTING" \
                        and settings.tab_process[cmd].status != "BACKOFF":
                        program = "program:" + cmd.split('_')[0]
                        logging.info("Start %s", cmd)
                        start_protected_launcher(settings.tab_prog[program], cmd, program, settings.tab_prog[program].startretries) 
                        clientsocket.send(("taskmasterd: Process "+ cmd + " is starting\n").encode("utf-8"))
                    else:
                        clientsocket.send(("taskmasterd: Process "+ cmd +" always running\n").encode("utf-8"))
                except KeyError:
                    clientsocket.send(("taskmasterd: No such program " + cmd).encode("utf-8"))
            clientsocket.send(("\r").encode("utf-8"))

        elif cmd_lst[0] == 'restart':
            for cmd in cmd_lst[1:]:
                try:
                    if settings.tab_process[cmd].status != "STARTING" and settings.tab_process[cmd].status != "RUNNING" \
                        and settings.tab_process[cmd].status != "BACKOFF":
                        clientsocket.send(("taskmasterd: Process " + cmd + " isn't running\n").encode("utf-8"))
                    else:
                        server.start_killer(copy.copy(settings.tab_process[cmd].pid))
                        clientsocket.send(("taskmasterd: Process "+ cmd + " is stopping\n").encode("utf-8"))
                    program = "program:" + cmd.split('_')[0]
                    logging.info("Restart %s", cmd)
                    start_protected_launcher(settings.tab_prog[program], cmd, program, settings.tab_prog[program].startretries) 
                    clientsocket.send(("taskmasterd: Process "+ cmd + " is starting\n").encode("utf-8"))
                except KeyError:
                    clientsocket.send(("taskmasterd: No such program " + cmd).encode("utf-8"))
            clientsocket.send(("\r").encode("utf-8"))

        elif cmd_lst[0] == 'stop':
            for cmd in cmd_lst[1:]:
                try:
                    if settings.tab_process[cmd].status != "STARTING" and settings.tab_process[cmd].status != "RUNNING" \
                            and settings.tab_process[cmd].status != "BACKOFF" and settings.tab_process[cmd].status != "STOPPING":
                        clientsocket.send(("taskmasterd: Process " + cmd + " isn't running\n").encode("utf-8"))
                    else:
                        logging.info("Stop %s", cmd)
                        server.start_killer(copy.copy(settings.tab_process[cmd].pid))
                        clientsocket.send(("taskmasterd: Process "+ cmd + " is stopping\n").encode("utf-8"))
                except KeyError:
                    clientsocket.send(("taskmasterd: No such process " + cmd + "\n").encode("utf-8"))
            clientsocket.send(("\r").encode("utf-8"))

        elif cmd_lst[0] == 'reload':
            logging.info("Reload server config : %s", cmd_lst[1])
            cleaner(server.list_progs)
            server.config = configparser.ConfigParser()
            try:
                if os.path.isfile(cmd_lst[1]) == False:
                    raise KeyError
                path_config = os.path.abspath(cmd_lst[1])
                server.config.read(path_config)
                old_list_progs = server.list_progs
                server.list_progs = extractProg(server.config.sections())
                if protect_stackoverflow(server.list_progs, server.config):
                    clientsocket.send("taskmasterd: Too much process asked, risk of stackoverlow, submit another config")
                else:
                    server.start_manager(server.config, server.list_progs, old_list_progs)
            except KeyError :
                clientsocket.send(("taskmasterd: No such file " + cmd_lst[1]).encode("utf-8"))
            clientsocket.send(("\r").encode("utf-8"))

        elif cmd_lst[0] == 'status':
            cleaner(server.list_progs)
            tab = getStatus(server.list_progs)
            for line in tab:
                clientsocket.send(line.encode("utf-8"))
            clientsocket.send(("\r").encode("utf-8"))

        elif cmd_lst[0] == 'config':
            for cmd in cmd_lst[1:]:
                try:
                    program = "program:" + cmd.split('_')[0]
                    conf = getConfig(server.config, program)
                    clientsocket.send(("[" + program + "]\n").encode("utf-8"))
                    for line in conf:
                        clientsocket.send((line + "\n").encode("utf-8"))
                except configparser.Error:
                    clientsocket.send(("taskmasterd: No such process " + cmd + "\n").encode("utf-8"))
            clientsocket.send(("\r").encode("utf-8"))

        elif cmd_lst[0] == 'log':
            try:
                f = open("/tmp/.taskmasterdlog", "r")
                i = 0
                for line in f:
                    i += 1
                f.seek(0, 0)
                try:
                    togo = i - int(cmd_lst[1])
                except IndexError:
                    togo = i - 10
                while togo > 0:
                    f.readline()
                    togo -= 1
                for line in f:
                    clientsocket.send(line.encode("utf-8"))
                f.close()
            except FileNotFoundError:
                clientsocket.send(("taskmasterd: No logging file").encode("utf-8"))
            clientsocket.send(("\r").encode("utf-8"))

        elif cmd_lst[0] == 'alert':
            try:
                start_manual_reporter(cmd_lst[1])
                clientsocket.send(("Mail sent !").encode("utf-8"))
                clientsocket.send("\r".encode("utf-8"))
            except IndexError:
                clientsocket.send(("taskmasterd : need a message").encode("utf-8"))
                clientsocket.send("\r".encode("utf-8"))
                

        elif cmd_lst[0] == 'attach':
            try:
                if settings.tab_process[cmd_lst[1]].status == "RUNNING":
                    try:
                        if settings.attach_process:
                            raise IndexError
                        settings.attach_process = cmd_lst[1]
                        time.sleep(2)
                        ioprocess(settings.tab_process[cmd_lst[1]], clientsocket)
                    except (IndexError,KeyError):
                        clientsocket.send("detach".encode("utf-8"))
                else:
                    clienstsocket.send("detach2".encode("utf-8"))
            except KeyError:
                clientsocket.send("detach".encode("utf-8"))  

        elif cmd_lst[0] == 'shutdown':
            for name in settings.tab_process:
                server.start_killer(settings.tab_process[name].pid)
            try:
                os.remove("/tmp/.taskmasterd")
            except:
                pass
            clientsocket.send(("Taskmasterd is shutdown").encode("utf-8"))
            clientsocket.send(("\r").encode("utf-8"))
            logging.info("Client %s exited", addr[1]) 
            logging.info("Taskmasterd server ended")
            os.kill(server.pid, signal.SIGKILL)

        else:
            clientsocket.send(("\r").encode("utf-8"))
