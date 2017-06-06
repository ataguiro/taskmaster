from taskmaster.debug import *

def extractProg(list_sections):
    prog = list()
    for sections in list_sections:
        if sections[0:7] == "program":
            prog.append(sections)
    return (prog)
