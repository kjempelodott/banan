from sys import stdout, stderr
import codecs

LOGLEVEL = 4
LOG = open('banan.log', 'w')
LOG.write('# -*- coding: utf-8 -*-\n\n')

def ERROR(msg, *lines):
    LOG.write('ERROR   : ' + msg + '\n')
    _MSG(*lines)

def WARN(msg, *lines):
    if LOGLEVEL > 1:
        LOG.write('WARNING : ' + msg + '\n')
        _MSG(*lines)

def INFO(msg, *lines):
    if LOGLEVEL > 2:
        LOG.write('INFO    : ' + msg + '\n')
        _MSG(*lines)

def DEBUG(msg, *lines):
    if LOGLEVEL > 3:
        LOG.write('DEBUG   : ' + msg + '\n')
        _MSG(*lines)

def _MSG(*lines):
    for line in lines:
        LOG.write(' '*10 + line + '\n')

