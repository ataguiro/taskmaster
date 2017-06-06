import os
import pwd
import grp

import logging

def drop_privileges():
    if os.getuid() == 0:
        running_uid = 1
        running_gid = 1

        os.setgroups([])

        os.setgid(running_gid)
        os.setuid(running_uid)

        logging.info('[DROP ROOT] Running with UID : ' + str(os.getuid()))
