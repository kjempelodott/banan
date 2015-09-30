import sys
from datetime import date
from buzhug import Base
from logger import INFO

class TransactionsDB:

    BASE = 'banan/transactions'

    def __init__(self, conf):
        self.config = conf
        self.open()

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

    def feed(self, fpath, parser, skip_duplicates=True, overwrite=False, dry_run=False):
        offset = self.db._pos.next_id
        deleted = added = 0
        for entry in parser.parse(fpath):
            if dry_run:
                print('%s %-40s\t%10.2f %s' % (entry['date'].isoformat(), 
                                               entry['account'][:40],
                                               entry['amount'], 
                                               entry['currency'])); continue

            if overwrite or skip_duplicates:
                _dup = self.db(date=entry['date'], account=entry['account'], amount=entry['amount'])
                if _dup:
                    if overwrite:
                        deleted += len(_dup)
                        self.db.delete(_dup)
                    else:
                        continue

            entry['label'] = self.config.assign_label(entry)
            self.insert(entry)
            added += 1
        
        if not dry_run:
            INFO('  added %i transactions' % added)
            INFO('  deleted %i transactions' % deleted)
            parser.post_process(self.db, offset=offset)              

