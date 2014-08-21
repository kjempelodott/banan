import re, locale

def configure(conf = 'labels.conf'):
    f = open(conf, 'r')
    coding = 'utf-8'
    try:
        coding = re.match('# -\*- coding: ([-\w]+) -\*-', f.readline()).groups()[0]
    except:
        print "WARNING: failed to read coding of config file, assuming utf-8"
        f.seek(0,0)
    labels = {}

    settings = {'local_currency':None,
                'foreign_currency_label':None,
                'incomes_label':'incomes',
                'cash_flow_ignore':[]}

    section = None
    for line in f.read().decode('utf-8').encode('utf-8').split('\n'):
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
                print "WARNING: setting '" + var + "' not recognized, skipping"
                continue
            settings[var] = val
            if var == 'cash_flow_ignore':
                settings[var] = [v.strip() for v in val.split(',')]
            continue
        print "Not able to parse line '" + line + "' in config"

    if not settings['local_currency'] and settings['foreign_currency_label']:
        print "WARNING: guessing local_currency from env"
        locale.setlocale(locale.LC_MONETARY, '')
        settings['local_currency'] = locale.localeconv()['int_curr_symbol']
        print "INFO: found '" + settings['local_currency'] + "'"
        
    return labels, settings
