import sys

def error_msg(msg):
    
    print("taskmasterd: " + msg, file=sys.stderr)
    sys.exit(-1)
