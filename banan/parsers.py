# -*- coding: utf-8 -*-

import re, os, csv
from datetime import date, datetime
from banan.logger import *
    

class Parser(object):

    RE_NO = re.compile(r'(^-?[\.\d]+?)([,\.](\d{1,2}))?$')
    
    @classmethod
    def read_file(cls, fpath):
        INFO('[%s] %s' % (cls.__name__, fpath))
        try:
            data = open(fpath, 'rb').read()
            return data
        except IOError: 
            ERROR('%s could not be opened for reading ' % fpath)
            raise SystemExit

    @staticmethod
    def parse_amount(value, sign=1):
        _value = value.replace(' ', '')
        try:
            m = Parser.RE_NO.match(_value).groups()
            _value = m[0].replace('.', '') + '.' + (m[2] if m[2] else '00')
            return sign * float(_value)
        except:
            ERROR('failed to parse amount \'%s\'' % value)

    @staticmethod
    def post_process(db, *args, **kw):
        pass


class CSVParser(Parser):
        
    @classmethod
    def parse(cls, fpath, sign):
        with open(fpath, newline='', encoding=cls.CHARSET) as csvfile:
            for row in csv.reader(csvfile, dialect='excel', delimiter=cls.DELIM):
                try:
                    date = datetime.strptime(row[cls.DATEIDX], cls.DATEFORMAT).date().isoformat()
                    account = row[cls.ACCTIDX]
                    amount = amount_local = sign * cls.parse_amount(row[cls.AMOUNTIDX])
                    currency = row[cls.CURRENCYIDX]
                    if cls.AMOUNTLCIDX != cls.AMOUNTIDX:
                        amount_local = sign * cls.parse_amount(row[cls.AMOUNTLCIDX])
                    amount, currency, amount_local = cls._parse(account, amount, currency, amount_local)
                    yield date, account, amount, amount_local, currency
                except ValueError as e:
                    print(e)

    @staticmethod
    def _parse(cls, *args):
        return args

class CustomCSVParser:
    @classmethod
    def parse(cls, fpath, *args):
        month = os.path.splitext(os.path.split(fpath)[-1])[0]
        date = datetime.strptime(month, '%Y_%m').date().isoformat()
        with open(fpath) as csvfile:
            for row in csv.reader(csvfile, dialect='excel', delimiter=';'):
                account = row[1]
                amount = int(row[2])
                yield date, account, amount, amount, 'NOK'

class yAbankCSVParser(CSVParser):

    CHARSET       = 'iso-8859-10'
    DATEFORMAT    = ' %d.%m.%Y'
    DELIM         = ','

    DATEIDX       = 0
    ACCTIDX       = 1
    AMOUNTIDX     = 3
    CURRENCYIDX   = -1
    AMOUNTLCIDX   = AMOUNTIDX

    @classmethod
    def _parse(cls, account, amount, currency, amount_local):
        # Special actions
        if account.startswith('Rentetransaksjon') or \
           account.startswith('Rentekapitalisering') or \
           account.startswith('Månedens rabatt') or \
           account.startswith('Innbetaling fra'):
            amount_local = abs(amount_local)
            amount = abs(amount)
        else:
            amount_local = -abs(amount_local)
            amount = -abs(amount)

        return amount, 'NOK', amount_local


class XLSParser(Parser):

    @classmethod
    def read_file(cls, fpath):
        import xlrd
        xls = xlrd.open_workbook(fpath)
        rows = xls.sheet_by_name(cls.SHEET).get_rows()
        # Throw away header
        next(rows)
        return xls.datemode, rows

    @classmethod
    def parse(cls, fpath, sign):
        import xlrd
        datemode, rows = cls.read_file(fpath)
        for row in rows:
            date = xlrd.xldate_as_datetime(row[cls.DATEIDX].value, datemode).isoformat()
            account = row[cls.ACCTIDX].value
            amount = amount_local = sign * row[cls.AMOUNTIDX].value
            currency = row[cls.CURRENCYIDX].value
            if cls.AMOUNTLCIDX != cls.AMOUNTIDX:
                amount_local = sign * row[cls.AMOUNTLCIDX].value
            yield date, account, amount, amount_local, currency


class BankNorwegianXLSParser(XLSParser):

    CHARSET       = 'utf-8'
    SHEET         = 'transactions'

    DATEIDX       = 0
    ACCTIDX       = 1
    AMOUNTIDX     = 3
    CURRENCYIDX   = 5
    AMOUNTLCIDX   = 6


class IkanoHTMLParser(Parser):

    CHARSET       = 'utf-16'
    DATEFORMAT    = '%d.%m.%Y'
    SKIP          = 1

    DATEIDX       = 0
    ACCTIDX       = 1
    AMOUNTIDX     = 7

    @classmethod
    def read_file(cls, fpath):
        from lxml import etree
        html = etree.HTML(open(fpath, encoding=cls.CHARSET).read())
        return html.find('body/table')

    @classmethod
    def parse(cls, fpath, sign):
        table = cls.read_file(fpath)
        for row in table.getchildren()[cls.SKIP:]:
            items = row.getchildren()
            date = items[cls.DATEIDX].getchildren()[0].text
            date = datetime.strptime(date, cls.DATEFORMAT).date().isoformat()
            account = items[cls.ACCTIDX].text
            currency = 'NOK'
            amount = items[cls.AMOUNTIDX].getchildren()[1].text
            amount = amount_local = sign * float(amount
                                                 .replace(' ','')
                                                 .replace(',','.'))
            yield date, account, amount, amount_local, currency
