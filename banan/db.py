import traceback, sys, re, sqlite3
from datetime import date, datetime
from urllib.parse import unquote_plus
from hashlib import sha1

from banan.logger import INFO, DEBUG


class TransactionsDB:

    STORAGE = 'banan/storage.db'

    def __init__(self, conf):
        self.config = conf
        self.db = sqlite3.connect(TransactionsDB.STORAGE)
        with self.db:
            self.db.cursor().execute("""
            CREATE TABLE IF NOT EXISTS Transactions (
              hash TEXT PRIMARY KEY,
              date DATE,
              account TEXT,
              amount REAL,
              amount_local REAL,
              currency TEXT,
              label TEXT
            )""")

    def feed(self, fpath, parser):
        with self.db:
            cur = self.db.cursor()
            for record in parser.parse(fpath):
                date, account, amount, amount_local, currency = record
                DEBUG('%s %-40s\t%12.2f %s' % (date,
                                               account[:40],
                                               amount,
                                               currency));

                label = self.config.assign_label(account, amount, currency)
                cur.execute("""
                INSERT OR IGNORE INTO Transactions
                  VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sha1(str(record).encode('utf-8')).hexdigest(), *record, label))

    def update_labels(self):
        with self.db:
            cur = self.db.cursor()
            data = cur.execute('SELECT hash, account, amount, currency, label FROM Transactions')
            for row in data.fetchall():
                _hash, account, amount, currency, _label = record
                label = self.config.assign_label(account, amount, currency)
                if label != _label:
                    cur.execute('UPDATE Transactions SET label=? WHERE hash=?', label, _hash)

    def process_data(self, data):
        array = []
        _sum = 0
        for record in data.fetchall():
            date, account, amount, amount_local, currency = record
            amount = '%.2f %s' % (amount, currency)
            _sum += amount_local
            array.append([date, account, amount])
        return _sum, array
    
    def assemble_data(self, period=None, labels=None):

        M = list(range(1,13))
        total = 0
        graph = {}
        text = {}
        sums = {}
        cur = self.db.cursor()

        try:
            if not labels:
                dates = re.findall('[0-9]{6}', unquote_plus(period))
                yyyy = int(dates[0][2:])
                mm = int(dates[0][:2])
                date1 = '%i-%02i-01' % (yyyy, mm)
                if len(dates) == 2:
                    yyyy = int(dates[1][2:])
                    mm = int(dates[1][:2])
                date2 = '%i-%i02-01' % (yyyy + (mm == 12), M[mm - 12])
                print(date1, date2)
                for label in self.config.labels.keys():
                    rows = cur.execute("""
                    SELECT date(date), account, amount, amount_local, currency FROM Transactions
                      WHERE label=?
                      AND date BETWEEN ? AND ?
                      ORDER BY date
                    """, (label, date1, date2))
                    _sum, data_array = self.process_data(rows)
                    if _sum:
                        graph[label] = _sum
                        if label not in self.config.cash_flow_ignore:
                            total += _sum
                        else:
                            label += '*'
                        text[label] = data_array
                        sums[label] = [_sum, self.config.local_currency]

            elif period in ('month', 'year'):
                date1 = date2 = first = datetime.now()
                if period == 'month':
                    first = date(date1.year - 1, date1.month, 1)
                    date1 = date(date1.year - (date1.month == 1), M[date1.month - 2], 1)
                    date2 = date(date2.year, date2.month, 1)
                else:
                    first = date(date1.year - 9, 1, 1)
                    date1 = date(date1.year, 1, 1)
                    date2 = date(date2.year + 1, 1, 1)

                label = unquote_plus(labels).split(',')
                while date1 >= first:
                    rows = cur.execute("""
                    SELECT date(date), account, amount, amount_local, currency FROM Transactions
                      WHERE label=?
                      AND date BETWEEN ? AND ?
                      ORDER BY date
                    """, (label, date1.isoformat(), date2.isoformat()))
                    date2 = date1 
                    if period == 'month':
                        key = date1.strftime('%Y.%m') 
                        date1 = date(date2.year - (date2.month == 1), M[date2.month - 2], 1)
                    else:
                        key = str(date1.year)
                        date1 = date(date2.year - 1, 1, 1)

                    _sum, data_array = self.process_data(rows)
                    graph[key] = _sum
                    total += _sum
                    if data_array:
                        text[label] = data_array
                        sums[label] = [_sum, self.config.local_currency]

            sums['==='] = total
            return True, {'text' : text, 'graph' : graph, 'sums' : sums}

        except Exception as e:
            traceback.print_tb(sys.exc_info()[2])
            return False, str(e)
