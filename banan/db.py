import sys
from datetime import date, datetime
from calendar import monthrange
from buzhug import Base
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
                              record.account[:40],
                              record.amount,
                              record.currency)); 
            try:
                idx += 1
                record = results[idx]
            except IndexError:
                return text_list

    
    def assemble_data(self, sid, datatype='plot', foreach='label', show='sum', data=None):

        if sid in self._sessions:
            if self._sessions[sid]['raw_query'] == (foreach, show, data):
                return self._sessions[sid]['flot'] if datatype == 'plot' else self._sessions[sid]['text']

        self._sessions[sid] = { 'raw_query' : (foreach, show, data) }
        get_amount = lambda rec: rec.amount_local

        if foreach == 'label':

            if not data: # Get last month
                now = datetime.now()
                from_date = date(now.year - (now.month == 1), range(1,13)[now.month - 2], 1)
                to_date = date(now.year, now.month, 1)
            else:
                from_date = date(data[0].year, data[0].month, 1)
                to_date = date(data[1].year + (data[1].month == 12), range(1,13)[data[1].month - 12], 1)

            data = {}
            text = {}
            select = 'dat1 <= date < dat2 and label == l'
            for label in self.config.labels.iterkeys():
                results = self.db.select(None, select, l = label, dat1 = from_date, dat2 = to_date)
                value = sum(map(get_amount, results))
                if abs(value) > 1:
                    text[label] = self.results_as_text(results)
                    strlen = len(text[label][-1])
                    sumstr = '%10.2f %s' % (value, self.config.local_currency)
                    text[label].append('-' * strlen)
                    text[label].append(' ' * (strlen - len(sumstr)) + sumstr)
                    data[label] = value

            if show == 'average':
                ydelta = to_date.year - from_date.year
                mdelta = to_date.month - from_date.month
                delta = 12 * ydelta + mdelta
                for key, val in data.iteritems():
                    data[key] /= delta

            self._sessions[sid]['flot'] = data
            self._sessions[sid]['text'] = text
            return self._sessions[sid]['flot'] if datatype == 'plot' else self._sessions[sid]['text']
            
        if foreach in ('month', 'year'):
            pass
            #result = self.db.select('\'%s\' in %s' % (foreach, data))

