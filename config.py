import re, locale
from logger import *


class Config:
    
    def __init__(self, conf = 'labels.conf'):
        
        self.local_currency = None
        self.foreign_currency_label = None
        self.incomes_label = 'incomes'
        self.others_label = 'other'
        self.cash_flow_ignore = []
        self.labels = {}

        self.coding = 'utf-8'
        self.parse_conf(conf)
        self.setup_local_currency()

    def parse_conf(self, conf):

        f = open(conf, 'r')
        try:
            self.coding = re.match('# -\*- coding: ([-\w]+) -\*-', f.readline()).groups()[0]
        except:
            WARN('assuming utf-8 encoded config file')
        f.seek(0,0)
  
        section = None
        SECTION = re.compile('^\[(.+)\]$')
        SETTING = re.compile('(\w+)=(.+)')

        content = f.readlines()
        if self.coding != 'utf-8':
            content = content.decode(self.coding).encode('utf-8').split('\n')
        for line in content:

            line = line.strip()
            if not line or line[0] == '#':
                continue 
               
            is_section = SECTION.match(line)
            if is_section:
                section = is_section.groups()[0]
                if section != 'settings':
                    self.labels[section] = []
                continue
            
            if section in self.labels:
                self.labels[section].append(line.replace('*','.*').strip())
                continue

            is_setting = SETTING.match(line)
            if is_setting:
                var, val = [x.strip() for x in is_setting.groups()]
                if hasattr(self, var):
                    setattr(self, var, val)
                    if var == 'cash_flow_ignore':
                        self.cash_flow_ignore = [v.strip() for v in val.split(',')]
                    continue
                WARN('[%s] setting not recognized' % var)
                continue
                                
            WARN('[line %s] in %s: unable to parse' % (line, conf))
 
    def setup_local_currency(self):
        if not self.local_currency and self.foreign_currency_label:
            INFO('guessing local_currency from env')
            locale.setlocale(locale.LC_MONETARY, '')
            self.local_currency = locale.localeconv()['int_curr_symbol']
            INFO('found \'%s\'' % self.local_currency)
        
    def assign_label(self, entry):
        matches = {}

        account = entry['account']
        for label, keywords in self.labels.iteritems():
            for kw in keywords:
                if re.sub(kw, '', account) != account:
                    matches[kw] = label
                    break

        if len(matches) == 1:
            return matches.popitem()[1]

        if not matches:
            currency = entry['currency']
            amount = entry['amount']
            if currency != self.local_currency and self.foreign_currency_label:
                return self.foreign_currency_label
            if amount > 0:
                return self.incomes_label
            return self.others_label
        
        label = matches[sorted(matches.keys(), key=len, reverse=True)[0]]
        rest = matches.values()
        rest.remove(label)
        WARN('[%s] matches several labels' % account,
             '  --> %s <--, %s ' % (label, ', '.join(rest)))
        return label
