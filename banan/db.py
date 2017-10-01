import sys, re
from datetime import date, datetime
from calendar import monthrange
from urllib.parse import unquote_plus
from copy import deepcopy

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

    def results_as_text(self, results):
        results = sorted(results, key=lambda rec: rec['date'])
        idx = 0
        record = results[idx]
        text_list = []
        while True:
            text_list.append('%s   %-40s\t%12.2f %s' %
                             (record['date'].isoformat(),
                              record['account'][:40],
                              record['amount'],
                              record['currency']));
            try:
                idx += 1
                record = results[idx]
            except IndexError:
                return text_list

    
    def assemble_data(self, datatype, foreach, show, select):

        try:
            get_amount = lambda rec: rec['amount_local']
            M = list(range(1,13))
            total = strlen = 0

            graph = {}
            text = {}
            average = {}
            
            if foreach == 'label':
                dates = re.findall('[0-9]{6}', unquote_plus(select))
                date1 = date2 = date(int(dates[0][2:]), int(dates[0][:2]), 1)
                if len(dates) == 2:
                    date2 = date(int(dates[1][2:]), int(dates[1][:2]), 1)
                date2 = date(date2.year + (date2.month == 12), M[date2.month - 12], 1)

                for label in self.config.labels.keys():
                    results = self.search((where('label') == label) &
                                          (date1 <= where('date') < date2))
                    value = sum(map(get_amount, results))
                    if abs(value) > 1:
                        graph[label] = value
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

                average = {}
                for key, val in graph.items():
                    average[key] = val/delta

            elif foreach in ('month', 'year'):
                date1 = date2 = first = datetime.now()
                if foreach == 'month':
                    first = date(date1.year - 1, date1.month, 1)
                    date1 = date(date1.year - (date1.month == 1), M[date1.month - 2], 1)
                    date2 = date(date2.year, date2.month, 1)
                else:
                    first = date(date1.year - 9, 1, 1)
                    date1 = date(date1.year, 1, 1)
                    date2 = date(date2.year + 1, 1, 1)

                label = unquote_plus(label)
                while date1 >= first:
                    results = self.search((where('label') == label) and
                                          (date1 <= where('date') < date2))
                    value = sum(map(get_amount, results))

                    date2 = date1 
                    if foreach == 'month':
                        key = date1.strftime('%Y.%m') 
                        date1 = date(date2.year - (date2.month == 1), M[date2.month - 2], 1)
                    else:
                        key = str(date1.year)
                        date1 = date(date2.year - 1, 1, 1)

                    graph[key] = value
                    total += value
                    if results:
                        text[key] = self.results_as_text(results)
                        strlen = len(text[key][-1])
                        sumstr = '%12.2f %s' % (value, self.config.local_currency)
                        text[key].append('-' * strlen)
                        text[key].append(' ' * (strlen - len(sumstr)) + sumstr)

            text['***'] = ['-' * strlen,
                           'SUM: %12.2f %s' % (total, self.config.local_currency),
                           '-' * strlen]
            return True, {'graph' : graph, 'text' : text, 'average' : average}

        except Exception as e:
            return False, str(e)
