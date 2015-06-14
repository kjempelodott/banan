import re, sys, datetime
from logger import *


def sorted_items(x):
    for key in sorted(x.keys()):
        yield key, x[key]


class Stats(object):

    def __init__(self, **kwargs):

        self.transactions = kwargs['transactions']
        self.labels       = kwargs['labels']
        self._settings    = kwargs['settings']

        self.reset()
        self.assign_labels()
        self.balance = 0

    def reset(self):
        self._lc        = self._settings['local_currency']
        self._fc_lbl    = self._settings['foreign_currency_label']
        self._in_lbl    = self._settings['incomes_label']
        self._ignore    = self._settings['cash_flow_ignore']
        self._other_lbl = self._settings['other_label']

        if self._fc_lbl: 
            self.labels[self._fc_lbl] = []

        self._ltr = dict((lbl, []) for lbl in self.labels.keys())
        self._ltr.update({self._fc_lbl    : [],
                          self._in_lbl    : [],
                          self._other_lbl : []})

    def update(self, transactions):
        self.assign_labels(transactions = transactions)

    def assign_labels(self, **kwargs):

        transactions = self.transactions
        if 'transactions' in kwargs:
            # Only assign labels to new transactions
            transactions = kwargs['transactions']
        else:
            # labels.conf has changed
            if ('labels' or 'settings') in kwargs:
                if 'labels' in kwargs:
                    self.labels = kwargs['labels']
                if 'settings' in kwargs:
                    self._settings = kwargs['settings']
                self.reset()

        for _hash, tr in transactions.iteritems():
            del tr.labels
            account = tr.account
            # Get all matches, but break after first match in each group
            for label, keywords in self.labels.iteritems():
                for kw in keywords:
                    if re.sub(kw, '', account) != account:
                        tr.add_label(label, kw)
                        break
            # No match, check if transaction is foreign or income, else label as other
            if not tr.labels:
                if tr.currency != self._lc and self._fc_lbl:
                    tr.add_label(self._fc_lbl)
                elif tr.amount > 0:
                    tr.add_label(self._in_lbl)
                else:
                    tr.add_label(self._other_lbl)
            # Get best match and add to label:transactions dict
            the_label = tr.get_best_match_label()
            self._ltr[the_label].append(tr)
            tr.cash_flow_ignore = the_label in self._ignore
            # If tr in transactions, remove it and update hash
            if _hash in self.transactions:
                del self.transactions[_hash]
            self.transactions[hash(tr)] = tr

                            
    def __str__(self):
        if not self.transactions:
            return 'NO TRANSACTIONS'
        if not self.balance:
            def ign(tr): return not tr.cash_flow_ignore
            self.balance = sum(tr.amount_local for tr in filter(ign, self.transactions))
                
        strlen = 5 + len(str(self.transactions[0])) + len(self._lc)
        sumstr = '_'*strlen + '\n' + ' '*(strlen-14) + '%10.2f %s\n'

        def prlbl(item): return len(item[1])
        ret = '\n'.join('[%s]\n' % lb + \
                        '   %s\n'   % '\n   '.join('%s %s' % (str(tr), self._lc) 
                                                   for tr in sorted(trs)) + \
                        '%s' % sumstr % (sum(tr.amount_local for tr in trs), self._lc) \
                        for (lb, trs) in filter(prlbl, sorted_items(self._ltr)))
        ret += (sumstr % (self.balance, self._lc)).replace('_','=')
        return ret

                
class Year(Stats, object):

    def __init__(self, year, stats):
        
        try:
            if year:
                self.year = int(year)
                assert(self.year <= datetime.date.today().year)
            else:
                self.year = datetime.date.today().year
            self._ltr       = stats._ltr
            self._lc        = stats._lc
            self._fc_lbl    = stats._fc_lbl
            self._in_lbl    = stats._in_lbl
            self._ignore    = stats._ignore
            self._other_lbl = stats._other_lbl
            
            self.balance = 0
            self._filter_year()
        except AssertionError:
            ERROR('Year %s is in future' % year)
            exit(0)
           
    def _filter_year(self):
        def filty(tr): return tr.date.year == int(self.year)
        self._ltr = dict((lb, filter(filty, trs)) for (lb, trs) in self._ltr.iteritems())
        self.transactions = reduce(lambda x, y: x+y, self._ltr.values())

            
class Month(Year, object):

    def __init__(self, year, month, stats):

        try:
            self.month = int(month)
            assert(self.month in range(1,13))
            self._ltr       = stats._ltr
            self._lc        = stats._lc
            self._fc_lbl    = stats._fc_lbl
            self._in_lbl    = stats._in_lbl
            self._ignore    = stats._ignore
            self._other_lbl = stats._other_lbl
            
            self.balance = 0
            self._filter_month()
            super(Month, self).__init__(year, self)
        except AssertionError:
            ERROR('\'%s\' is not a valid month' % month)
            exit(0)

    def _filter_month(self):
        def filtm(tr): return tr.date.month == self.month
        self._ltr = dict((lb, filter(filtm, trs)) for (lb, trs) in self._ltr.iteritems())
        self.transactions = reduce(lambda x, y: x+y, self._ltr.values())
