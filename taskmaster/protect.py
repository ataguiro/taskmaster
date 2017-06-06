import configparser

import taskmaster.settings as settings

def protect_stackoverflow(list_progs, config):
    
    count = 0
    for programs in list_progs:
        try:
            count += int(config.get(programs, "numprocs"))
            if count > 200:
                return True
        except configparser.NoOptionError:
            count += 1

    return False
