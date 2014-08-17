import re, sys

class Stats(object):

    class Error(Exception):

        def __init__(self):
            print """ 
 __init__ got garbage arguments

 Usage: Stats(transactions, conf):
    transactions = dict {str, Transaction}
    conf         = dict {str, list[str]  }
"""

    def __init__(self, transactions, conf):

        try:
            self.__transactions__ = transactions
            self.__groups__ = {'inntekt':[],'utland':[]}
            self.assign_groups(conf)
        except:
            raise Stats.Error()

    def assign_groups(self, conf):
        self.__groups__.update(dict((g,[]) for g in conf.keys()))
        for tr in self.__transactions__.values():
            tr.reset_groups()
            if tr.amount > 0:
                tr.add_group('inntekt')
                self.__groups__['inntekt'].append(tr)
                continue
            account = tr.account.upper();
            for group, keywords in conf.items():
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

                
class Year(Stats, object):

    def __init__(self, year, **kwargs):

        conf, transactions = [None, None]
        for key, arg in kwargs:
            if key == "conf" and type(arg) == dict:
                conf = arg
            elif key == "transactions" and type(arg) == dict:
                self.__transactions__ = arg
            elif key == "stats" and type(stats) == Stats:
                self = stats
                return

        super(Year, self).__init__(transactions, conf)
        self.__filter_year__(self, year)

        self.__year__ = year
        def get_year(self): return self.__year__
        year = property(get_year, None, None)

    def __filter_year__(self, year):
        for md5, tr in transactions.items():
            if tr.get_date_object().year != int(year):
                del self.__transactions__[md5]


class Month(Year, object):

    def __init__(self, year, month, **kwargs):

        super(Month, self).__init__(year, **kwargs)
        self.__filter_month__(self, month)

        self.__month__ = month
        def get_month(self): return self.__month__
        month = property(get_month, None, None)

    def __filter_month__(self, month):
        for md5, tr in transactions.items():
            if tr.get_date_object().month != int(month):
                del self.__transactions__[md5]
