import sys, re
from datetime import date, datetime
from calendar import monthrange
from buzhug import Base
from urllib import unquote
from copy import deepcopy

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
        offset = self.db._pos.next_id
        deleted = added = 0
        for entry in parser.parse(fpath):
            if dry_run:
                print('%s %-40s\t%10.2f %s' % (entry['date'].isoformat(), 
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
            parser.post_process(self.db, offset=offset)


    # Queries
    get_amount = lambda rec: rec.amount_local    

    def results_as_text(self, results):

        results.sort_by('date')
        idx = 0
        record = results[idx]
        text_list = []
        while True:
            text_list.append('%s   %-40s\t%10.2f %s' %
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

            session = self._sessions.get(sid, None)
            if session:
                if session['raw_query'] == (foreach, show, select):
                    # Same query, return cached result
                    return True, \
                        self._sessions[sid]['flot_' + show] if datatype == 'plot' else \
                        self._sessions[sid]['text']

            get_amount = lambda rec: rec.amount_local

            if foreach == 'label':
                
                if session:
                    if session['raw_query'][0] == 'label' and session['raw_query'][2] == select:
                        # Same query, but different presentation (sum or average)
                        return True, \
                            self._sessions[sid]['flot_' + show] if datatype == 'plot' else \
                            self._sessions[sid]['text']

                # New query
                dates = re.findall('[0-9]{6}', unquote(select))
                date1 = date2 = date(int(dates[0][2:]), int(dates[0][:2]), 1)
                if len(dates) == 2:
                    date2 = date(int(dates[1][2:]), int(dates[1][:2]), 1)
                if date2 == date1:
                    date2 = date(date1.year + (date1.month == 12), range(1,13)[date1.month - 12], 1)

                data = {}
                text = {}
                balance = 0
                strlen = 0
                query = 'date1 <= date < date2 and label == l'

                for label in self.config.labels.iterkeys():

                    results = self.db.select(None, query, l = label, date1 = date1, date2 = date2)
                    value = sum(map(get_amount, results))

                    if abs(value) > 1:
                        data[label] = value

                        if label not in self.config.cash_flow_ignore:
                            balance += value
                        else:
                            label += '*'

                        text[label] = self.results_as_text(results)
                        strlen = len(text[label][-1])
                        sumstr = '%10.2f %s' % (value, self.config.local_currency)
                        text[label].append('-' * strlen)
                        text[label].append(' ' * (strlen - len(sumstr)) + sumstr)

                # All good, set new session attributes
                session = self._sessions[sid] = { 'raw_query' : (foreach, show, select) }
                session['date1'], session['date2'] = date1, date2
                session['flot_sum'] = data
                session['text'] = text

                ydelta = date2.year - date1.year
                mdelta = date2.month - date1.month
                delta = 12 * ydelta + mdelta

                session['flot_average'] = {}
                for key, val in session['flot_sum'].iteritems():
                    session['flot_average'][key] = val/delta

                if text:
                    session['text']['***'] = ['-' * strlen,
                                              'SUM: %10.2f %s' % (balance, self.config.local_currency),
                                              '-' * strlen]

                return True, session['flot_' + show] if datatype == 'plot' else session['text']
    

            if foreach in ('month', 'year'):
                raise 
                #result = self.db.select('\'%s\' in %s' % (foreach, data))

            raise
            
        except Exception as e:
            return False, str(e)
                

    def clean_sessions(self):
        self._sessions.clear()
