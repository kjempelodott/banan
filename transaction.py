import re, datetime

class Transaction(object):

    def __init__(self):
         
        self.__account__          = ''
        self.__amount__           = 0
        self.__amount_local__     = 0
        self.__date__             = datetime.date.today()
        self.__currency__         = ''
        self.__labels__           = {}
        self.__re_no__            = r'(-?[\.\d]+),(\d\d)'
        self.__cash_flow_ignore__ = False

    def get_cash_flow_ignore(self): return self.__cash_flow_ignore__    
    def set_cash_flow_ignore(self, value): 
        self.__cash_flow_ignore__ = value
    cash_flow_ignore = property(get_cash_flow_ignore, None, None)
    
    def get_account(self): return self.__account__    
    def set_account(self, value): 
        self.__account__ = value
    account = property(get_account, None, None)

    def get_amount(self): return self.__amount__
    def set_amount(self, value, sign=1): 
        try:
            m = re.match(self.__re_no__, value).groups()
            value = m[0].replace('.','') + '.' + (m[1] if m[1] else '00')
        except:
            pass
        self.__amount__ = sign*float(value)
    amount = property(get_amount, None, None)

    def get_amount_local(self): return self.__amount_local__
    def set_amount_local(self, value, sign=1): 
        try:
            m = re.match(self.__re_no__, value).groups()
            value = m[0].replace('.','') + '.' + (m[1] if m[1] else '00')
        except:
            pass
        self.__amount_local__ = sign*float(value)
    amount_local = property(get_amount_local, None, None)

    def get_date_object(self): return self.__date__
    def get_date(self): return self.__date__.isoformat() 
    def set_date(self, value): 
        self.__date__ = value
    date = property(get_date, None, None)

    def get_currency(self): return self.__currency__    
    def set_currency(self, value): 
        self.__currency__ = value
    currency = property(get_currency, None, None)    

    def add_label(self, label, kw = 'dummy'):
        self.__labels__[kw] = label
    def get_labels(self):
        return self.__labels__.values()
    def get_best_match_label(self):
        if len(self.__labels__) > 1:
            label = self.__labels__[sorted(self.__labels__.keys(), 
                                    key=len, reverse=True)[0]]
            print "WARNING: transaction matches more than one label\n" \
                " %s\n   -> %s\n" % (self.__account__, 
                                     ', '.join(self.__labels__.values())) + \
                " assigning to", label
            return label
        return self.__labels__.values()[0]
    def reset_labels(self):
        self.__labels__ = {}
    labels = property(get_labels, None, reset_labels)    
    
    def __cmp__(self, other):
        return cmp(self.__date__.toordinal(), other.__date__.toordinal())

    def __str__(self):
        return "%s %-40s\t%10.2f" % (self.date, self.account[:40], 
                                     self.amount_local)
