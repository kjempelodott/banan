# -*- coding: utf-8 -*-
import re, os, datetime
from HTMLParser import HTMLParser
from transaction import Transaction
from logger import *
from hashlib import md5

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
            yyyy = datetime.date.now().year

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
        _last = None
        for page in data[1:]:
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
                transaction.date = datetime.date(int(yyyy), int(mm), int(dd))
                _last = hash(transaction)
                transactions[_last] = transaction
                pos = match.end()
                match = get_match(page)
            # End of page, set pos to 0
            pos = 0

        # Remove last entry, which is the sum
        del transactions[_last]
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
            transaction.date = datetime.date(int(yyyy), int(mm), int(dd))
            transactions[hash(transaction)] = transaction

        return transactions


class BankNorwegianCSVParser(_Parser, object):

    CHARSET = 'utf-8'
    FILEEXT = '.csv'
    DIR     = './banknorwegian/'

    @staticmethod
    def parse(data):
        data = data.decode(BankNorwegianCSVParser.CHARSET).encode('utf-8')
        transactions = {}
        for line in data.split('\n')[1:]:
            if not line:
                continue
            line = line.split(';')
            date = line[0]
            mm, dd, yyyy = date.split('/')
            account = line[1]
            amount = line[3]
            currency = line[5]
            amount_local = line[6]          

            transaction = Transaction()
            transaction.account = account
            transaction.set_amount(amount)
            transaction.set_amount_local(amount_local)
            transaction.currency = currency
            transaction.date = datetime.date(int(yyyy), int(mm), int(dd))
            transactions[hash(transaction)] = transaction

        return transactions


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

