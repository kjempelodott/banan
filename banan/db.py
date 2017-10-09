import traceback, sys, re
from datetime import date, datetime
from urllib.parse import unquote_plus

from tinydb import TinyDB, where
from tinydb.utils import iteritems
from tinydb_serialization import Serializer, SerializationMiddleware

from banan.logger import INFO, DEBUG


class DateTimeSerializer(Serializer):
    OBJ_CLASS = date

    def encode(self, obj):
        return obj.strftime('%Y-%m-%d')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%d').date()


class TransactionsDB(TinyDB):

    STORAGE = 'banan/storage.json'

    def __init__(self, conf):
        self.config = conf
        serialization = SerializationMiddleware()
        serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
        super().__init__(TransactionsDB.STORAGE, storage=serialization)

    def feed(self, fpath, parser):
        for record in parser.parse(fpath):
            DEBUG('%s %-40s\t%12.2f %s' % (record['date'].isoformat(),
                                           record['account'][:40],
                                           record['amount'],
                                           record['currency']));

            self.config.assign_label(record)
            self.insert(record)

    def update_labels(self):
        rawdata = self._read()
        data = {}
        for eid, el in iteritems(rawdata):
            self.config.assign_label(el)
            data[eid] = el
        self._write(data)

    def to_arrays(self, data):
        data = sorted(data, key=lambda rec: rec['date'])
        arrays = []
        for record in data:
            date = record['date'].isoformat()
            amount = '%.2f %s' % (record['amount'], record['currency'])
            arrays.append([date, record['account'], amount])
        return arrays
    
    def assemble_data(self, period=None, labels=None):

        get_amount = lambda rec: rec['amount_local']
        M = list(range(1,13))
        total = 0
        graph = {}
        text = {}
        sums = {}

        try:
            if not labels:
                dates = re.findall('[0-9]{6}', unquote_plus(period))
                date1 = date2 = date(int(dates[0][2:]), int(dates[0][:2]), 1)
                if len(dates) == 2:
                    date2 = date(int(dates[1][2:]), int(dates[1][:2]), 1)
                date2 = date(date2.year + (date2.month == 12), M[date2.month - 12], 1)
                print(date1, date2)
                for label in self.config.labels.keys():
                    results = self.search((where('label') == label) &
                                          (date1 <= where('date')) &
                                          (where('date') < date2))
                    value = sum(map(get_amount, results))
                    if abs(value) > 1:
                        graph[label] = value
                        if label not in self.config.cash_flow_ignore:
                            total += value
                        else:
                            label += '*'
                        text[label] = self.to_arrays(results)
                        sums[label] = [value, self.config.local_currency]

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
                    results = self.search((where('label') == label) &
                                          (date1 <= where('date')) &
                                          (where('date') < date2))
                    value = sum(map(get_amount, results))

                    date2 = date1 
                    if period == 'month':
                        key = date1.strftime('%Y.%m') 
                        date1 = date(date2.year - (date2.month == 1), M[date2.month - 2], 1)
                    else:
                        key = str(date1.year)
                        date1 = date(date2.year - 1, 1, 1)

                    graph[key] = value
                    total += value
                    if results:
                        text[label] = self.to_arrays(results)
                        sums[label] = [value, self.config.local_currency]

            sums['==='] = total
            return True, {'text' : text, 'graph' : graph, 'sums' : sums}

        except Exception as e:
            traceback.print_tb(sys.exc_info()[2])
            return False, str(e)
