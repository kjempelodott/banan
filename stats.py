import re, sys

class Error(Exception):

    def __init__(self):
        print """ 
 __init__ got garbage arguments

 Stats, Year and Month must get **kwargs:
    transactions = dict {str, Transaction}
    conf         = dict {str, list[str]  }
    OR
    Stats object [Month and Year]
"""

class Stats(object):

    def __init__(self, transactions, conf):

        try:
            self.__transactions__ = transactions
            self.__groups__ = {'inntekt':[],'utland':[]}
            self.assign_groups(conf)
        except:
            raise Error()

    def assign_groups(self, conf):
        self.__groups__.update(dict((g,[]) for g in conf.keys()))
        for tr in self.__transactions__.values():
            tr.reset_groups()
            if tr.amount > 0:
                tr.add_group('inntekt')
                self.__groups__['inntekt'].append(tr)
                continue
            account = tr.account.upper();
            for group, keywords in conf.iteritems():
                for kw in keywords:
                    if re.sub(kw,'',account) != account:
                        tr.add_group(group)
                        break
            if tr.currency != 'NOK' and not tr.groups:
                tr.add_group('utland')
            if len(tr.groups) > 1:
                print "WARNING: transaction mathces more than one group\n" + \
                    " %s\n  in %s\n" % (tr.account, tr.groups) + \
                    " will assign to",tr.groups[0]
            if tr.groups:
                self.__groups__[tr.groups[0]].append(tr)

    def get_transactions(self):
        return self.__transactions__
    transactions = property(get_transactions, None, None)
    def get_groups(self):
        return self.__groups__
    groups = property(get_groups, None, None)

                
class Year(Stats, object):

    def __init__(self, year, **kwargs):
        
        self.__year__ = year
        try:
            self.__transactions__ = kwargs["transactions"]
            self.__conf__ = kwargs["conf"]
            self.__filter__(False)
            super(Year, self).__init__(transactions, conf)
        except:
            try:
                self.__transactions__ = kwargs["stats"].transactions
                self.__groups__ = kwargs["stats"].groups
                self.__filter__()
            except:
                raise Error()

    def get_year(self): return self.__year__
    year = property(get_year, None, None)

    def __filter__(self, filter_groups=True):
        self.__transactions__ = dict((md5,tr) for (md5,tr) in self.transactions.iteritems() if tr.get_date_object().year != int(self.year))
        if filter_groups:
            def f(tr): return tr.get_date_object().year == int(self.year)
            self.__groups__ = dict((gr,filter(f,trs)) for (gr,trs) in self.groups.iteritems())


class Month(Year, object):

    def __init__(self, year, month, **kwargs):

        self.__month__ = month
        try:
            self.__transactions__ = kwargs["transactions"]
            self.__conf__ = kwargs["conf"]
            self.__filter__(False)
            super(Month, self).__init__(year, **kwargs)
        except:
            super(Month, self).__init__(year, **kwargs)
            self.__filter_month__()

    def get_month(self): return self.__month__
    month = property(get_month, None, None)

    def __filter__(self, filter_groups=True):
        self.__transactions__ = dict((md5,tr) for (md5,tr) in self.transactions.iteritems() if tr.get_date_object().month != int(self.month))
        if filter_groups:
            def f(tr): return tr.get_date_object().month == int(self.month)
            self.__groups__ = dict((gr,filter(f,trs)) for (gr,trs) in self.groups.iteritems())
