import re, sys, datetime

def sorted_items(x):
    for key in sorted(x.keys()):
        yield key, x[key]


class Error(Exception):

    def __init__(self):
        self.message = """ 
 __init__ got garbage arguments

 Stats(transactions, labels, settings)
 Year(year, **kwargs)
 Month(year, month, **kwargs)

 year <= %i
 1 <= month <= 12

 **kwargs:
    transactions = dict {str, Transaction}
    labels       = dict {str, list[str]  }
    settings     = dict {str, str        }
    OR
    stats        = Stats object
""" % datetime.date.today().year

    def __str__(self):
        return self.message


class Stats(object):

    def __init__(self, **kwargs):

        try:
            self.__transactions__ = kwargs['transactions']
            labels = kwargs['labels']
            settings = kwargs['settings']
            self.__labels__ = {settings['incomes_label']:[], 'annet':[]}
            self.__lc__ = settings['local_currency']
            self.__fcl__ = settings['foreign_currency_label']
            self.__ignore__ = settings['cash_flow_ignore']
            if self.__fcl__: self.__labels__[self.__fcl__] = []
            self.assign_labels(labels, settings)
            self.balance = 0
        except:
            raise Error

    def assign_labels(self, labels, settings):
        self.__labels__.update(dict((g,[]) for g in labels.keys()))
        for tr in self.__transactions__.values():
            tr.reset_labels()
            account = tr.account
            for label, keywords in labels.iteritems():
                for kw in keywords:
                    if re.sub(kw,'',account) != account:
                        tr.add_label(label)
                        if label in self.__ignore__:
                            tr.cash_flow_ignore = True
                        break
            if not tr.labels:
                if tr.currency != self.__lc__ and self.__fcl__:
                    tr.add_label(self.__fcl__)
                elif tr.amount > 0:
                    tr.add_label(settings['incomes_label'])
                else:
                    tr.add_label('annet')
            if len(tr.labels) > 1:
                print "WARNING: transaction matches more than one label\n" + \
                    " %s\n   -> %s\n" % (tr.account, ', '.join(tr.labels)) + \
                    " will assign to",tr.labels[0]
            if tr.labels:
                self.__labels__[tr.labels[0]].append(tr)

    def get_transactions(self):
        return self.__transactions__
    transactions = property(get_transactions, None, None)
    def get_labels(self):
        return self.__labels__
    labels = property(get_labels, None, None)

    def __str__(self):
        if not self.__transactions__:
            return 'NO TRANSACTIONS'
        if not self.balance:
            def f(tr): return not tr.cash_flow_ignore
            self.balance = sum(tr.amount_local for tr in filter(f, self.transactions.values()))

        strlen = 5+len(str(self.__transactions__.values()[0]))+len(self.__lc__)
        sumstr = '_'*strlen + '\n' + ' '*(strlen-14) + '%10.2f %s\n'

        ret = '\n'.join("[%s]\n   %s\n%s" % (lb,
                                             "\n   ".join("%s %s" % (str(tr), self.__lc__) for tr in sorted(trs)), 
                                             sumstr % (sum(tr.amount_local for tr in trs), self.__lc__)) 
                        for (lb,trs) in sorted_items(self.labels) if trs)
        ret+= (sumstr % (self.balance, self.__lc__)).replace('_',"=")
        return ret

                
class Year(Stats, object):

    def __init__(self, year, **kwargs):
        
        try:
            assert(int(year) <= datetime.date.today().year)
            self.__year__ = int(year)
            self.__transactions__ = kwargs['transactions']
            self.__filter_year__(False)
            kwargs['transactions'] = self.__transactions__
            super(Year, self).__init__(**kwargs)
        except AssertionError:
            raise Error
        except:
            try:
                st = kwargs['stats']
                self.__transactions__ = st.transactions
                self.__labels__ = st.labels
                self.__lc__ = st.__lc__
                self.__fcl__ = st.__fcl__
                self.balance = 0
                self.__filter_year__()
            except:
                raise Error
           
    def get_year(self): return self.__year__
    year = property(get_year, None, None)

    def __filter_year__(self, filter_labels=True):
        def f(tr): return tr.get_date_object().year == int(self.year)
        self.__transactions__ = dict(zip(self.transactions.keys(), filter(f, self.transactions.values())))
        if filter_labels:
            self.__labels__ = dict((lb,filter(f,trs)) for (lb,trs) in self.labels.iteritems())

            
class Month(Year, object):

    def __init__(self, year, month, **kwargs):

        try:
            assert(int(month) in range(1,13))
            self.__month__ = int(month)
            self.__transactions__ = kwargs['transactions']
            self.__filter_month__(False)
            kwargs['transactions'] = self.__transactions__
            super(Month, self).__init__(year, **kwargs)
        except AssertionError:
           raise Error
        except:
           super(Month, self).__init__(year, **kwargs)
           self.__filter_month__()

    def get_month(self): return self.__month__
    month = property(get_month, None, None)

    def __filter_month__(self, filter_labels=True):
        def f(tr): return tr.get_date_object().month == self.month
        self.__transactions__ = dict(zip(self.transactions.keys(), filter(f, self.transactions.values())))
        if filter_labels:
            self.__labels__ = dict((lb,filter(f,trs)) for (lb,trs) in self.labels.iteritems())
