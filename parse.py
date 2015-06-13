# -*- coding: utf-8 -*-
import re, os, datetime
from HTMLParser import HTMLParser
from hashlib import md5
from transaction import Transaction
from logger import *

class _Parser(object):

    @classmethod
    def update(cls, files, stats):
        for f in os.listdir(cls.DIR):
            try:
                if os.path.splitext(f)[1] != cls.FILEEXT:
                    continue
                f = cls.DIR + f
                data = open(f, 'rb').read()
                _md5 = md5(data).hexdigest()
                if not files.has_key(f) or files[f] != _md5:
                    stats.update(cls.parse(data))
                    files[f] = _md5
                    INFO('Successfully parsed ' + f)
            except IOError: 
                ERROR('Could not open file ' + f)


class yAbankPDFParser(_Parser, object):

    FILEEXT = '.pdf'
    DIR     = './yabank/'
    # TODO: does not match "innbetaling m/kid 4.799,99 ...."
    _RE_CREDIT = re.compile(r'(?P<date>\d\d\.\d\d)' \
                             '(?P<account>.{1,40}?)\d\d\.\d\d' \
                             '(?P<amount>[\.\d]+,\d\d)')
    _RE_DEBIT  = re.compile(r'(?P<account>.{1,40}?)' \
                             '(?P<date>\d\d\.\d\d)' \
                             '(?P<amount>[\.\d]+,\d\d)')

    @staticmethod
    def parse(data):
        data = yAbankPDFParser.convert(data).split("Side:")[1:]
        try:
            yyyy = int(re.search("Saldo pr\. \d\d\.\d\d\.(\d\d\d\d)kr", data[0]).groups()[0])
        except:
            WARNING('Failed to extract year from PDF')
            yyyy = datetime.datetime.now().year

        transactions = {}
        pos, match = 0, 0
        credit, debit = yAbankPDFParser._RE_CREDIT, yAbankPDFParser._RE_DEBIT

        def get_match(page):
            match = [credit.search(page, pos), debit.search(page, pos)]
            if match[0] and match[1]:
                return match[match[0].end() > match[1].end()]
            else:
                return match.remove(None) or match[0]

        transactions = {}
        for n, page in enumerate(data[1:]):
            match = get_match(page)
            while match:
                gr = match.groupdict()
                if u'favør' in unicode(gr['account'], 'utf-8'):
                    pos = match.end()
                    match = get_match(page)
                    continue
                sign = (1,-1)[match.re == credit]
                dd, mm = gr['date'].split('.')

                transaction = Transaction()
                transaction.account = gr['account']
                transaction.set_amount(gr['amount'], sign)
                transaction.amount_local = transaction.amount
                transaction.currency = 'NOK'
                transaction.date = datetime.datetime(int(yyyy), int(mm), int(dd))
                transactions[md5(str(transaction)).hexdigest()] = transaction

                pos = match.end()
                match = get_match(page)
            # End of page, set pos to 0
            pos = 0

        return transactions

    @staticmethod
    def convert(data):
        from pdfminer.pdfinterp import PDFResourceManager, process_pdf
        from pdfminer.converter import TextConverter
        from StringIO import StringIO
        pdfdata = StringIO(data)
        htmldata = StringIO()
        man = PDFResourceManager()
        conv = TextConverter(man, htmldata)
        process_pdf(man, conv, pdfdata)
        data = htmldata.seek(0) or htmldata.read()
        return data

            
class yAbankCSVParser(_Parser, object):

    CHARSET = 'iso-8859-10'
    FILEEXT = '.csv'
    DIR     = './yabank/'
    _RE_NONLOC  = re.compile(r"^VISA .+ \d\d.\d\d (\D+) (\d+,\d\d) .+$")

    @staticmethod
    def parse(data):
        data = data.decode(yAbankCSVParser.CHARSET).encode('utf-8')
        transactions = {}
        for line in data.split('\n'):
            if not line:
                continue
            line = line.split(';')
            date = line[1]
            dd, mm, yyyy = date.split('-')
            account = line[2]
            amount_local = amount = line[3]
            currency = 'NOK'
            try:
                currency, amount = yAbankCSVParser._RE_NONLOC.match(account).groups()
            except:
                pass

            transaction = Transaction()
            transaction.account = account
            transaction.set_amount(amount)
            transaction.amount_local = transaction.amount
            transaction.currency = currency
            transaction.date = datetime.datetime(int(yyyy), int(mm), int(dd))
            transactions[md5(str(transaction)).hexdigest()] = transaction

        return transactions


class BankNorwegianHTMLParser(_Parser, HTMLParser, object):

    CHARSET = 'iso-8859-1'
    FILEEXT = '.html'
    DIR     = './banknorwegian/'

    def __init__(self):

        self._DATE        =   1
        self._ACCOUNT     =   2
        self._AMOUNT      =   8
        self._CURRENCY    =  16

        super(BankNorwegianHTMLParser, self).__init__()
        self.transactions = {}
        self._in_table = False
        self._in_tr = False
        self._data = 0
        self._this = {}

    @staticmethod
    def parse(data):
        data = data.replace('&nbsp;','')
        inst = BankNorwegianHTMLParser()
        inst.feed(data)
        return inst.transactions

    def handle_starttag(self, tag, attrs):
        self._data = 0
        # New transaction
        if self._in_table and tag == 'tr' and ('class', '') in attrs:
            self._in_tr = True
            self._transaction = Transaction()
        # Data
        elif self._in_tr:
            if tag == 'td':
                if ('class', 'date') in attrs:
                    self._data = self._DATE
                elif ('class', 'amount') in attrs:
                    self._data = self._AMOUNT
                elif ('data-bind', "text: isCurrencyTx() ? currencyAmountText: ''") in attrs:
                    self._data = self._CURRENCY
            elif tag == 'div' and ('data-bind', 'text: transactionMainText') in attrs:
                    self._data = self._ACCOUNT
        # Start of a transaction table
        elif tag == 'table' and attrs == [('class', 'table table-hover transactions')]:
            self._in_table = True

    def handle_endtag(self, tag):
        # End of transaction
        if  tag == 'tr' and self._in_tr:
            self.transactions[md5(str(self._transaction)).hexdigest()] = self._transaction
            self._in_tr = False
        self._data = 0

    def handle_data(self, data):
        if not self._data:
            return

        data = data.decode(BankNorwegianHTMLParser.CHARSET).encode('utf-8')
        data = data.strip()
            
        # Set date
        if self._data & self._DATE:
            dd, mm, yy = data.split('.')
            self._transaction.date = datetime.datetime(int('20' + yy), int(mm), int(dd))
        # Set account
        elif self._data & self._ACCOUNT:
            self._transaction.account = data
        # Set amount
        elif self._data & self._AMOUNT:
            self._transaction.currency = 'NOK'
            self._transaction.set_amount(data, -1)
            self._transaction.amount_local = self._transaction.amount
        # Set currency
        elif self._data & self._CURRENCY:
            amount, currency = data.split()
            self._transaction.currency = currency
            self._transaction.set_amount(amount, -1)


"""
A   <kjop>  [kode] [varenavn] [antall] [pris] [nest siste tall: 2 (intern), 1 (ekstern)] *[tull]
J   <retur>  ...
B 30 SIGN.ANNUL <annulert>

R   <sum>
x   <mva>
 <  <slutt: tid og sum>
"""

class ZRapport(object):

    @staticmethod
    def parse(data):
        tickets = {}
        this = None
        for line in data.split('\n'):
            if not line:
                continue
            if line[0:2] in ['A ','J ']:
                try:
                    name = line[7:28].strip()
                    n = int(line[28:32])
                    price = float(line[32:43])
                    is_intern = bool(int(line[54]) - 1)
                    this = md5(line).hexdigest()
                    tickets[this] = [name, n, price, is_intern]
                except Exception as e:
                    WARNING('Failed to parse \'line\'')
                    continue
            elif line[0:17] == "B   30 SIGN.ANNUL":
                del tickets[this]
            elif line[0:2] == " <":
                this = None
        return tickets

