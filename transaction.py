import re, datetime
from logger import *
from hashlib import md5

class Transaction(object):

    def __init__(self):
         
        self.account           = ''
        self.date              = datetime.date.today()
        self.currency          = ''
        self.cash_flow_ignore = False
        self._amount           = 0
        self._amount_local     = 0
        self._labels           = {}
        self._hash             = 0
        self._RE_NO            = re.compile(r'(^-?[\.\d]+?)([,\.](\d{1,2}))?$')
        # example: 99,90 ('99', ',90', '90')

    def get_amount(self): return self._amount
    def set_amount(self, _value, sign = 1): 
        value = _value.replace(' ', '')
        try:
            m = self._RE_NO.match(value).groups()
            value = m[0].replace('.','') + '.' + (m[2] if m[2] else '00')
            self._amount = sign*float(value)
        except:
            DEBUG('failed to parse amount: ' + _value)
    def set_parsed_amount(self, parsed_value):
        self._amount = parsed_value
    amount = property(get_amount, set_parsed_amount, None)

    def get_amount_local(self): return self._amount_local
    def set_amount_local(self, _value, sign = 1): 
        value = _value.replace(' ', '')
        try:
            m = self._RE_NO.match(value).groups()
            value = m[0].replace('.','') + '.' + (m[2] if m[2] else '00')
        except:
            DEBUG('failed regexp amount ' + value)
        self._amount_local = sign*float(value)
    def set_parsed_amount_local(self, parsed_value):
        self._amount_local = parsed_value
    amount_local = property(get_amount_local, set_parsed_amount_local, None)

    def add_label(self, label, kw = 'dummy'):
        self._hash = 0
        self._labels[kw] = label
    def get_labels(self):
        return set(self._labels.values())
    def reset_labels(self):
        self._labels = {}
    labels = property(get_labels, None, reset_labels)    

    def get_best_match_label(self):
        if len(self._labels) > 1:
            label = self._labels[sorted(self._labels.keys(), key=len, reverse=True)[0]]
            WARN('transaction (%s) matches more than one label' % self.account)
            INFO('matches are \'%s\'' % '\', \''.join(self._labels.values()))
            INFO('assigning to \'' + label + '\'')
            return label
        return self._labels.values()[0]
    
    def __cmp__(self, other):
        return cmp(self.date.toordinal(), other.date.toordinal())

    def __str__(self):
        return '%s %-40s\t%10.2f' % (self.date.isoformat(), self.account[:40], self.amount_local)

    def __hash__(self):
        if not self._hash:
            self._hash = int(md5(self.__str__()).hexdigest(), 16)
        return self._hash
        
