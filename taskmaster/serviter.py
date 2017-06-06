import socket
import logging

import taskmaster.settings

from taskmaster.debug import * 
from taskmaster.services import *

num_threads = 0

def serviter(clientsocket, addr, server):
    global num_threads

    retries = 3
    while retries > 0:
        answer = (clientsocket.recv(1024)).decode('utf-8')
        if answer == server.psswd:
            clientsocket.send(("valid").encode("utf-8"))
            retries = 0 
            services(clientsocket, addr, server)
        
        retries -= 1
        if retries == 0:
            clientsocket.send(("Too many false submits, deconnecting").encode("utf-8"))
            break
        elif retries > 0:
            clientsocket.send(("Wrong password, submit again").encode("utf-8"))

    num_threads -= 1
    logging.info("Client %s exited", addr[1]) 
    clientsocket.close()
