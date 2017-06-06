import os
import sys
import signal
import resource

from taskmaster.task_error import *
from taskmaster.debug import *

def daemon_success(number, frame):
    sys.exit(0)

def daemonize():

    # Check already living taskmasterd 

    try:
        pidfile = open('/tmp/.taskmasterd', 'r')
        pid = int(pidfile.readline())
        if  pid > 0:
            error_msg("Taskmasterd already alive")
    except FileNotFoundError:
        pass

    fatherpid = os.getpid()
    status = os.fork()

    if status > 0:
       signal.signal(signal.SIGUSR1, daemon_success)
       os.wait()

    # Set process as new session leader and process group leader
    
    if status == 0:
        os.setsid()

        # Fork again to prevent reacquisition of a controlling terminal

        status = os.fork()
        
        if status > 0:
            sys.exit()
        
        # Close all file descriptors

        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE);
        while soft > 2:
            try:
                os.close(soft)
            except:
                pass
            soft -= 1
            
       # Open standard fd on /dev/null

        fd = open('/dev/null')
        os.dup2(fd.fileno(), 0)
        os.dup2(fd.fileno(), 1)
#        os.dup2(fd.fileno(), 2)

        # Reset umask and current directory

        os.umask(0)
        os.chdir('/')
    
        # Write pid to ensure non co-existing same daemon

        pidfile = open('/tmp/.taskmasterd', 'w+')
        pid = os.getpid() 
        pidfile.write(str(pid))

        os.kill(fatherpid, signal.SIGUSR2) 
