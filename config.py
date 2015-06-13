import re, locale
from logger import *


def configure(conf = 'labels.conf'):
    f = open(conf, 'r')
    coding = 'utf-8'
    try:
        coding = re.match('# -\*- coding: ([-\w]+) -\*-', f.readline()).groups()[0]
    except:
        WARN('failed to read config file encoding .. assuming utf-8')
        f.seek(0,0)
    labels = {}

    settings = {'local_currency'         : None,
                'foreign_currency_label' : None,
                'incomes_label'          : 'incomes',
                'other_label'            : 'other',
                'cash_flow_ignore'       : []}

    section = None
    for line in f.read().decode(coding).encode('utf-8').split('\n'):
        if not line or line[0] == '#':
            continue                
        lm = re.match('^\[(.+)\]$', line)
        if lm:
            section = lm.groups()[0]
            if section != 'settings':
                labels[section] = []
            continue
        if labels.has_key(section):
            labels[section].append(line.replace('*','.*').strip())
            continue
        sm = re.match('(\w+)=(.+)', line)
        if sm:
            var, val = [x.strip() for x in sm.groups()]
            if not settings.has_key(var):
                WARN('setting \'%s\' not recognized .. skipping' % var)
                continue
            settings[var] = val
            if var == 'cash_flow_ignore':
                settings[var] = [v.strip() for v in val.split(',')]
            continue
        WARN('Not able to parse line \'%s\' in config' % line)

    if not settings['local_currency'] and settings['foreign_currency_label']:
        INFO('guessing local_currency from env')
        locale.setlocale(locale.LC_MONETARY, '')
        settings['local_currency'] = locale.localeconv()['int_curr_symbol']
        INFO('found \'%s\'' % settings['local_currency'])
        
    return labels, settings
