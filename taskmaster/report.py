import time
import smtplib
import threading

from email.mime.text import MIMEText

import taskmaster.settings as settings

from taskmaster.debug import *

def start_reporter(name_prog):
    t = threading.Thread(target=reporter, args=(name_prog, None))
    t.start()

def start_manual_reporter(name_prog):
    t = threading.Thread(target=manual_reporter, args=(name_prog, None))
    t.start()

def reporter(name, null):
    DG(str(settings.opt))
    if settings.opt != 1:
        return 
    me = 'taskmaster@42.fr'
    you = 'ataguiro@student.42.fr'

    now = time.strftime("%c")
    msg = MIMEText(str(now) + ', program "' + name + '" crashed !')

    msg['Subject'] = '[CRASH] Program [' + name  + '] crashed !'
    msg['From'] = me
    msg['To'] = you

    try:
        s = smtplib.SMTP('smtp.neuf.fr')
        s.sendmail(me, you, msg.as_string())
        s.quit()
    except:
        pass

def manual_reporter(name, null):
    if settings.opt != 1:
        return 
    me = 'taskmasterd@42.fr'
    you = "originadam@gmail.com"

    now = time.strftime("%c")
    msg = MIMEText(str(now) + " : " + str(name)  + ".")  
  
    msg['Subject'] = '[MANUAL ALERT]'
    msg['From'] = me
    msg['To'] = you

    try:
        s = smtplib.SMTP('smtp.neuf.fr')
        s.sendmail(me, you, msg.as_string())
        s.quit()
    except:
        pass
