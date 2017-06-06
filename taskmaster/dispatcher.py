import os
import time
import logging
from select import select

import taskmaster.settings as settings

from taskmaster.debug import *
from taskmaster.task_error import *

def dispatcher():

    while 1: 

        my_fds = list()
        for fd in settings.fds:
            if settings.attach_process and settings.tab_process[settings.attach_process].process_fd[1] != fd and \
            settings.tab_process[settings.attach_process].process_fd[2] != fd:
                my_fds.append(fd)

            elif settings.attach_process == 0:
                my_fds.append(fd)


        if len(my_fds) > 0:
            try:
                rfds, wfds, xfds = select(my_fds, [], [])
            except (ValueError, OSError):
                logging.info("Taskmasterd server ended")
                error_msg("No more fd")

        for fd in my_fds:
            if fd in rfds:
                try:
                    data = os.read(fd, 1024) 
                    if data:
                        filename = settings.fd2realfile[fd]
                        try:
                            tmp_fd = os.open(filename, os.O_CREAT | os.O_WRONLY | os.O_APPEND)
                            os.write(tmp_fd, data)
                            os.close(tmp_fd)
                        except IsADirectoryError:
                            pass
                    if not data:
                        if fd in settings.queue_old_fd:
                            try:
                                i = settings.fds.index(fd)
                                settings.fds.pop(i)
                                i = settings.queue_old_fd.index(fd)
                                settings.queue_old_fd.pop(i)
                                os.close(fd)
                            except OSError:
                                pass 
                except BlockingIOError:
                    pass
        time.sleep(1)
