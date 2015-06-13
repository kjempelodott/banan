from sys import stdout, stderr

LOGLEVEL=4

def ERROR(msg):
    stderr.write('ERROR : ' + msg + '\n')

def WARN(msg):
    if LOGLEVEL > 1:
        stdout.write('WARNING : ' + msg + '\n')

def INFO(msg):
    if LOGLEVEL > 2:
        stdout.write('INFO  : ' + msg + '\n')

def DEBUG(msg):
    if LOGLEVEL > 3:
        stdout.write('DEBUG : ' + msg + '\n')

