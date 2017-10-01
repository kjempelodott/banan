import re, locale
from banan.logger import *

class Config:
    
    def __init__(self, conf = 'labels.conf'):
        
        self.local_currency = None
        self.foreign_currency_label = None
        self.incomes_label = 'incomes'
        self.others_label = 'other'
        self.cash_flow_ignore = []
        self.labels = {}
        self.parse_conf(conf)
        self.setup_currency()
        self.labels[self.incomes_label] = []
        self.labels[self.others_label] = []

    def parse_conf(self, conf):

        f = open(conf, 'rb')
        f.seek(0,0)
  
        section = None
        SECTION = re.compile('^\[(.+)\]$')
        SETTING = re.compile('(\w+)=(.+)')

        content = f.read().decode().split('\n')
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
                self.labels[section].append(
                    re.compile(line.lower().replace('*','.*').strip())
                )
                continue

            is_setting = SETTING.match(line)
            if is_setting:
                var, val = [x.strip() for x in is_setting.groups()]
                if hasattr(self, var):
                    setattr(self, var, val)
                    if var == 'cash_flow_ignore':
                        self.cash_flow_ignore = [v.strip() for v in val.split(',')]
                    continue
                WARN('unknwon setting \'%s\'' % var)
                continue
                                
            WARN('unable to parse:\n  %s' % line)
 
    def setup_currency(self):
        if self.foreign_currency_label and not self.local_currency:
            locale.setlocale(locale.LC_MONETARY, '')
            self.local_currency = locale.localeconv()['int_curr_symbol']
            INFO('using local_currency from env: %s' % self.local_currency)

    def assign_label(self, record):
        matches = {}
        account = record['account'].lower()
        for label, keywords in self.labels.items():
            for kw in keywords:
                if kw.sub('', account) != account:
                    matches[kw] = label
                    break

        if len(matches) == 1:
            record['label'] = matches.popitem()[1]
            return

        if not matches:
            currency = record['currency']
            amount = record['amount']
            if currency != self.local_currency and self.foreign_currency_label:
                record['label'] = self.foreign_currency_label
            elif amount > 0:
                record['label'] = self.incomes_label
            else:
                record['label'] = self.others_label
            return
        
        relen = lambda r: len(r.pattern)
        label = matches[sorted(matches.keys(), key=relen, reverse=True)[0]]
        rest = list(matches.values())
        rest.remove(label)
        INFO('%s\n  matches several labels\n  \033[1m%s\033[0m, %s' %
             (record['account'], label, ', '.join(rest)))
        record['label'] = label
