from sys import stdout, stderr
from time import strftime

LOGLEVEL = 4
LOG      = open('banan.log', 'w')
LOG.write('# -*- coding: utf-8 -*-\n\n')

def ERROR(msg, *lines):
    msg = 'ERROR   : ' + msg + '\n'
    stderr.write(msg)
    _write(msg)
    _msg(*lines)

def WARN(msg, *lines):
    if LOGLEVEL > 1:
        _write('WARNING : ' + msg + '\n')
        _msg(*lines)

def INFO(msg, *lines):
    if LOGLEVEL > 2:
        _write('INFO    : ' + msg + '\n')
        _msg(*lines)

def DEBUG(msg, *lines):
    if LOGLEVEL > 3:
        _write('DEBUG   : ' + msg + '\n')
        _msg(*lines)

def _msg(*lines):
    for line in lines:
        LOG.write(' '*21 + line + '\n')

def _write(msg):
    LOG.write('[%s] %s' % (strftime('%H:%M:%S'), msg))
