import socket
import readline
import os
import sys
import configparser 
import getpass
import signal

from taskmaster.debug import *
from taskmaster.attach import *

# Line editing inits

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')
readline.parse_and_bind('Meta-h: backward-kill-word')
readline.parse_and_bind('"\C-u": universal-argument')
readline.parse_and_bind('set horizontal-scroll-mode On')

# host and port config


def header():
	print("  _______        _                        _            ")
	print(" |__   __|      | |                      | |           ")
	print("    | | __ _ ___| | ___ __ ___   __ _ ___| |_ ___ _ __ ")
	print("    | | (_| \__ \   <| | | | | | (_| \__ \ ||  __/ |   ")
	print("    |_|\__,_|___/_|\_\_| |_| |_|\__,_|___/\__\___|_|   ")
	print("                            by ariard, ataguiro        ")
	print("")

def welcome(cnum):
	header()
	print("----------------------------------------------------------------")
	print("-- Available commands : help, start [command], restart [command]")
	print("--                      status [command], stop, exit            ")
	print("--                      reload [file]                           ")
	print("-- Server running adress : ", host                               )
	print("-- Listening on port : ", port                                   )
	print("-- You are the client number : ", cnum                           )
	print("----------------------------------------------------------------")

def line_is_command(line):
    if (line == "exit" or line == "help" or "start" in line or "restart" in line or "status" in line \
        or "stop" in line or "reload" in line or line == "shutdown" or "config" in line or "alert" in line \
        or "alert" in line or "attach" in line or "log" in line):
        return 1
    return 0

def exit_client(number, frame):
    print("Exiting client...")
    sys.exit(0)

def wait_answer(sc):
    while True:
        try:
            reply = sc.recv(1024).decode('utf-8')
        except ConnectionResetError:
            raise ConnectionResetError
        if len(reply) > 0 and reply != '\r':
            print(reply.rstrip("\n\r"))
        if "\r" in reply:
            break

def prompt(sc):
    while True: 
        try:
            line = input("\033[1;32mtaskmaster>\033[0m ")
            if (line_is_command(line)):
                if "reload" in line:
                    sp = line.split()
                    if len(sp) == 2:
                        sp[1] = os.path.abspath(sp[1])
                        line = sp[0] + " " + sp[1]
                sc.send(line.encode('utf-8'))             
                word = line.split(' ')[0]
                if (line == 'exit'):
                    break
                elif "attach" == word:
                    attach_mode(sc)
                else:
                    try:
                        wait_answer(sc)
                    except ConnectionResetError:
                        print("Broken connection, exiting")
                        break
            elif (line == 'help'):
                print ("exit, start <prog>, restart <prog>, status <prog>, stop <prog>, reload <file>, help")
            else:
                print("taskmaster:", line, ": command not found")
        except EOFError:
            sys.stdout.write("\n")
            pass 

def launch(host, port):
    signal.signal(signal.SIGINT, exit_client)
    sc = socket.socket()
    print("Trying to connect", host, "on port", port," ...")
    try:
        sc.connect((host, port))
    except ConnectionRefusedError:
        sys.stderr.write("taskmasterctl: No server listening on this given port")
        sys.exit(1)
    try:
        sc.send(("\r\n").encode('utf-8'))
        cnum = (sc.recv(1024)).decode('utf-8')
    except ConnectionResetError:
        sys.stderr.write("taskmasterctl : Unexpected reset connection by server")
        sys.exit(1)
    welcome(cnum)
    i = 3
    while True:
        try:
            psswd = getpass.getpass()
            if len(psswd) == 0:
                psswd = "\r\n"
            sc.send(psswd.encode('utf-8'))
            answer = sc.recv(1024).decode('utf-8')
            if answer == "valid":
                prompt(sc)
                sys.exit(0)
            print(answer)
            if "deconnecting" in answer:
                sys.exit(-1)
        except EOFError:
            i -= 1
            if i == 0:
                print("Too many false submits, deconnecting")
                sys.exit(-1)
            pass


if __name__ == '__main__':
    try:
        path_config = os.path.abspath(sys.argv[1])
    except:
        sys.stderr.write("taskmasterctl: No such configuration file")
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(path_config)
    try:
        host = config.get('server', 'host')
    except (configparser.NoSectionError, configparser.NoOptionError):
        sys.stderr.write("taskmasterctl: No field server - host")
        sys.exit(1)
    try:
        port = int(config.get('server', 'port'))
    except (configparser.NoSectionError, configparser.NoOptionError):
        sys.stderr.write("taskmasterctl: No field server - port")
        sys.exit(1)
    launch(host, port)
