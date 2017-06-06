import os
import sys
import pty
import tty
import time
import fcntl
from select import select

import taskmaster.settings as settings

from taskmaster.debug import *

def remove_tmp_fd(out, err):
    pos = settings.fds.index(out)
    settings.fds.pop(pos)
    pos = settings.fds.index(err)
    settings.fds.pop(pos)

def writen(fd, data):
    while data:
        n = os.write(fd, data)
        data = data[n:]

def ioprocess(process, clientsocket):

    try:
        os.unlink("/tmp/.client_attach")
        os.unlink("/tmp/.server_attach")
    except FileNotFoundError:
        pass
    fd_client = os.open("/tmp/.client_attach", os.O_CREAT | os.O_RDONLY)
    fd_server = os.open("/tmp/.server_attach", os.O_CREAT | os.O_WRONLY)
    clientsocket.send("synchro".encode('utf-8'))
    in_process = process.process_fd[0] 
    out_process = process.process_fd[1] 
    fcntl.fcntl(out_process, fcntl.F_SETFL, os.O_NONBLOCK)
    err_process = process.process_fd[2] 
    fcntl.fcntl(err_process, fcntl.F_SETFL, os.O_NONBLOCK)
    remove_tmp_fd(out_process, err_process)
    fileout = settings.fd2realfile[out_process]
    fileerr = settings.fd2realfile[err_process]
    tmp_fdout = os.open(fileout, os.O_CREAT | os.O_WRONLY | os.O_APPEND)
    tmp_fderr = os.open(fileerr, os.O_CREAT | os.O_WRONLY | os.O_APPEND)
    while True:

        fds = [fd_client, out_process, err_process] 

        rfds, wfds, xfds = select(fds, [], [])

        if fd_client in rfds:
            data = os.read(fd_client, 1024)
            if data.decode("utf-8") == "detach":
                break
            if data:
                data = data.decode("utf-8")
                os.write(in_process, data.encode("utf-8") + "\n".encode("utf-8"))

        if out_process in rfds:
            try:
                data = os.read(out_process, 1024)
            except BlockingIOError:
                pass
            if data:
                data = data.decode("utf-8")
                writen(fd_server, data.encode("utf-8"))
                writen(tmp_fdout, data.encode("utf-8"))

        if err_process in rfds:
            try:
                data = os.read(err_process, 1024)
            except BlockingIOError:
                pass
            if data:
                data = data.decode("utf-8")
                writen(fd_server, data.encode("utf-8"))
                writen(tmp_fderr, data.encode("utf-8"))
    settings.fds.append(out_process)
    settings.fds.append(err_process)
    settings.attach_process = 0
    os.close(fd_client)
    os.close(fd_server)
