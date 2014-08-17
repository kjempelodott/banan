import re, sys, datetime


def sorted_items(x):
    for key in sorted(x.keys()):
        yield key, x[key]


class Error(Exception):

    def __init__(self):
        self.message = """ 
 __init__ got garbage arguments

 Stats(transactions, conf)
 Year(year, **kwargs)
 Month(year, month, **kwargs)

 year <= %i
 1 <= month <= 12

 **kwargs:
    transactions = dict {str, Transaction}
    conf         = dict {str, list[str]  }
    OR
    stats        = Stats object
""" % datetime.date.today().year

    def __str__(self):
        return self.message


class Stats(object):

    def __init__(self, transactions, conf):

        try:
            self.__transactions__ = transactions
            self.__groups__ = {'inntekter':[],'utland':[]}
            self.assign_groups(conf)
        except:
            raise Error
        self.sum = sum(tr.amount_local for tr in self.transactions.values()) 

    def assign_groups(self, conf):
        self.__groups__.update(dict((g,[]) for g in conf.keys()))
        for tr in self.__transactions__.values():
            tr.reset_groups()
            if tr.amount > 0:
                print tr.amount, tr.currency
                tr.add_group('inntekter')
                self.__groups__['inntekter'].append(tr)
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
                print "WARNING: transaction matches more than one group\n" + \
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

    def __str__(self):
        ret = '\n'.join("[%s]\n   %s\n" % (gr,'\n   '.join(str(tr) for tr in sorted(trs))) for (gr,trs) in sorted_items(self.groups))
        strlen = 4+len(str(self.__transactions__.values()[0]))
        ret+= '-'*strlen
        ret+= '\n%s%-10.2f\n' % (' '*(strlen-9), self.sum)
        return ret

                
class Year(Stats, object):

    def __init__(self, year, **kwargs):
        
        try:
            assert(int(year) <= datetime.date.today().year)
            self.__year__ = int(year)
            self.__transactions__ = kwargs["transactions"]
            self.__conf__ = kwargs["conf"]
            self.__filter_year__(False)
            super(Year, self).__init__(transactions, conf)
        except AssertionError:
            raise Error
        except:
            try:
                self.__transactions__ = kwargs["stats"].transactions
                self.__groups__ = kwargs["stats"].groups
                self.__filter_year__()
            except:
                raise Error
        self.sum = sum(tr.amount_local for tr in self.transactions.values()) 
           
    def get_year(self): return self.__year__
    year = property(get_year, None, None)

    def __filter_year__(self, filter_groups=True):
        self.__transactions__ = dict((md5,tr) for (md5,tr) in self.transactions.iteritems() if tr.get_date_object().year == int(self.year))
        if filter_groups:
            def f(tr): return tr.get_date_object().year == int(self.year)
            self.__groups__ = dict((gr,filter(f,trs)) for (gr,trs) in self.groups.iteritems())

            
class Month(Year, object):

    def __init__(self, year, month, **kwargs):

        try:
            assert(int(month) in range(1,13))
            self.__month__ = int(month)
            self.__transactions__ = kwargs["transactions"]
            self.__conf__ = kwargs["conf"]
            self.__filter_month__(False)
            super(Month, self).__init__(year, **kwargs)
        except AssertionError:
            raise Error
        except:
            super(Month, self).__init__(year, **kwargs)
            self.__filter_month__()
        self.sum = sum(tr.amount_local for tr in self.transactions.values()) 

    def get_month(self): return self.__month__
    month = property(get_month, None, None)

    def __filter_month__(self, filter_groups=True):
        self.__transactions__ = dict((md5,tr) for (md5,tr) in self.transactions.iteritems() if tr.get_date_object().month == self.month)
        if filter_groups:
            def f(tr): return tr.get_date_object().month == self.month
            self.__groups__ = dict((gr,filter(f,trs)) for (gr,trs) in self.groups.iteritems())
