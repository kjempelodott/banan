import sys
from datetime import date
from buzhug import Base

class TransactionsDB:

    BASE = 'db/transactions'

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

    def feed(self, fpath, parser, skip_duplicates = True, overwrite = False):
        offset = self.db._pos.next_id
        for entry in parser.parse(fpath):
            if skip_duplicates or overwrite:
                _dup = self.db(date=entry['date'], account=entry['account'], amount=entry['amount'])
                if _dup:
                    if skip_duplicates:
                        continue
                    self.db.delete(_dup)
            entry['label'] = self.config.assign_label(entry)
            self.insert(entry)
            
        parser.post_process(self.db, offset=offset)                

