import sys, re
from datetime import date, datetime
from calendar import monthrange
from buzhug import Base
from urllib import unquote_plus
from copy import deepcopy
from logger import INFO

class TransactionsDB(object):

    BASE = 'banan/transactions'

    def __init__(self, conf):
        self.config = conf
        self._sessions = {}
        self.open()

    # Management
    def open(self):
        self.db = Base(TransactionsDB.BASE)
        try:
            self.db.open()
        except IOError:
            self.db.create(('amount'      , float), 
                           ('amount_local', float),
                           ('date'        , date),
                           ('account'     , str),
                           ('label'       , str),
                           ('currency'    , str))

    def close(self):
        self.db.close()
            
    def clearall(self):
        self.db.destroy()
        self.open()
        
    def insert(self, entry):
        self.db.insert(amount       = entry['amount'],
                       amount_local = entry['amount_local'],
                       date         = entry['date'],
                       account      = entry['account'],
                       label        = entry['label'],
                       currency     = entry['currency'])

    def feed(self, fpath, parser, skip_duplicates=True, overwrite=False, delete=False, dry_run=False):

        deleted = added = 0
        for entry in parser.parse(fpath):
            if dry_run:
                print('%s %-40s\t%12.2f %s' % (entry['date'].isoformat(),
                                               entry['account'][:40],
                                               entry['amount'], 
                                               entry['currency'])); continue

            if skip_duplicates or overwrite or delete:
                _dup = self.db(date=entry['date'], account=entry['account'], amount=entry['amount'])
                if _dup:
                    if overwrite or delete:
                        deleted += len(_dup)
                        self.db.delete(_dup)
                    else:
                        continue
                if delete:
                    continue

            entry['label'] = self.config.assign_label(entry)
            self.insert(entry)
            added += 1
        
        if not dry_run:
            INFO('  added %i transactions' % added)
            INFO('  deleted %i transactions' % deleted)
            parser.post_process(self.db, added)

    def update_labels(self):
        
        # Load all records into memory. File will get corrupt if using the iterator.
        records = [rec for rec in self.db]
        for record in records:
            as_dict = dict((field, getattr(record, field)) for field in record.fields)
            label = self.config.assign_label(as_dict)
            if label != record.label:
                self.db.update(record, label=label)

        self.db.cleanup()


    # Queries
    get_amount = lambda rec: rec.amount_local    

    def results_as_text(self, results):

        results.sort_by('date')
        idx = 0
        record = results[idx]
        text_list = []
        while True:
            text_list.append('%s   %-40s\t%12.2f %s' %
                             (record.date.isoformat(), 
                              unicode(record.account[:40], 'utf-8'),
                              record.amount,
                              record.currency)); 
            try:
                idx += 1
                record = results[idx]
            except IndexError:
                return text_list

    
    def assemble_data(self, sid, datatype, foreach, show, select):

        try:

            session = self._sessions.get(sid, {})
            if session:
                if session['raw_query'] == (foreach, show, select):
                    # Same query, return cached result
                    return True, \
                        self._sessions[sid]['flot_' + show] if datatype == 'plot' else \
                        self._sessions[sid]['text']

            # Helpers
            get_amount = lambda rec: rec.amount_local
            M = range(1,13)
            total = strlen = 0

            data = {}
            text = {}
            query = 'date1 <= date < date2 and label == l'

            if foreach == 'label':
                
                if session:
                    if session['raw_query'][0] == 'label' and session['raw_query'][2] == select:
                        # Same query, but different presentation (sum or average)
                        return True, \
                            self._sessions[sid]['flot_' + show] if datatype == 'plot' else \
                            self._sessions[sid]['text']

                # New query
                dates = re.findall('[0-9]{6}', unquote_plus(select))
                date1 = date2 = date(int(dates[0][2:]), int(dates[0][:2]), 1)
                if len(dates) == 2:
                    date2 = date(int(dates[1][2:]), int(dates[1][:2]), 1)
                date2 = date(date2.year + (date2.month == 12), M[date2.month - 12], 1)

                for label in self.config.labels.iterkeys():

                    results = self.db.select(None, query, l = label, date1 = date1, date2 = date2)
                    value = sum(map(get_amount, results))

                    if abs(value) > 1:
                        data[label] = value

                        if label not in self.config.cash_flow_ignore:
                            total += value
                        else:
                            label += '*'

                        text[label] = self.results_as_text(results)
                        strlen = len(text[label][-1])
                        sumstr = '%12.2f %s' % (value, self.config.local_currency)
                        text[label].append('-' * strlen)
                        text[label].append(' ' * (strlen - len(sumstr)) + sumstr)

                ydelta = date2.year - date1.year
                mdelta = date2.month - date1.month
                delta = 12 * ydelta + mdelta

                session['flot_average'] = {}
                for key, val in data.iteritems():
                    session['flot_average'][key] = val/delta


            elif foreach in ('month', 'year'):
                
                # New query
                date1 = date2 = first = datetime.now()
                if foreach == 'month':
                    first = date(date1.year - 1, date1.month, 1)
                    date1 = date(date1.year - (date1.month == 1), M[date1.month - 2], 1)
                    date2 = date(date2.year, date2.month, 1)
                else:
                    first = date(date1.year - 9, 1, 1)
                    date1 = date(date1.year, 1, 1)
                    date2 = date(date2.year + 1, 1, 1)

                select = unquote_plus(select)

                while date1 >= first:

                    results = self.db.select(None, query, l = select, date1 = date1, date2 = date2)
                    value = sum(map(get_amount, results))

                    date2 = date1 
                    if foreach == 'month':
                        key = date1.strftime('%Y.%m') 
                        date1 = date(date2.year - (date2.month == 1), M[date2.month - 2], 1)
                    else:
                        key = str(date1.year)
                        date1 = date(date2.year - 1, 1, 1)

                    data[key] = value
                    total += value
                    if results:
                        text[key] = self.results_as_text(results)
                        strlen = len(text[key][-1])
                        sumstr = '%12.2f %s' % (value, self.config.local_currency)
                        text[key].append('-' * strlen)
                        text[key].append(' ' * (strlen - len(sumstr)) + sumstr)


            # All good, set new session attributes
            session['raw_query'] = (foreach, show, select)
            session['flot_sum'] = data
            session['text'] = text

            if session['text']:
                session['text']['***'] = ['-' * strlen,
                                          'SUM: %12.2f %s' % (total, self.config.local_currency),
                                          '-' * strlen]

            self._sessions[sid] = session
            return True, session['flot_' + show] if datatype == 'plot' else session['text']

        except Exception as e:
            return False, str(e)
