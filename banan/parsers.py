# -*- coding: utf-8 -*-

import re, os
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


class yAbankPDFParser(Parser):

    # TODO: does not match "innbetaling m/kid 4.799,99 ...." yes, it does?!
    RE_CREDIT = \
        re.compile(r'(?P<date>\d\d\.\d\d)(?P<account>.{1,40}?)\d\d\.\d\d(?P<amount>[\.\d]+,\d\d)')
    RE_DEBIT  = \
        re.compile(r'(?P<account>.{1,40}?)(?P<date>\d\d\.\d\d)(?P<amount>[\.\d]+,\d\d)')

    RE_YYYY   = re.compile('Saldo pr\. \d\d\.\d\d\.(\d\d\d\d)kr')
    YYYY      = int()


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


    @staticmethod
    def set_year(pre):
        try:
            yAbankPDFParser.YYYY = int(yAbankPDFParser.RE_YYYY.search(pre).groups()[0])
        except:
            WARN('failed to extract year from pdf')
            yAbankPDFParser.YYYY = date.today().year

    @staticmethod
    def parse(fpath):
        data = yAbankPDFParser.read_file(fpath)
        data = yAbankPDFParser.convert(data).split("Side:")[1:]
        yAbankPDFParser.set_year(data.pop(0))

        page_pos = 0

        for page in data:

            def get_entry():
                global entry
                entry = [yAbankPDFParser.RE_CREDIT.search(page, page_pos), 
                         yAbankPDFParser.RE_DEBIT.search(page, page_pos)]

                if entry[0] and entry[1]:
                    entry = entry[entry[0].end() > entry[1].end()]
                else:
                    entry = entry.remove(None) or (None if not entry else entry[0])

            get_entry()
            while entry:
                fields = entry.groupdict()
                if 'favør' in fields['account']:
                    page_pos = entry.end()
                    get_entry()
                    continue
                
                sign = (1,-1)[entry.re == yAbankPDFParser.RE_CREDIT]
                dd, mm = fields['date'].split('.')

                amount = sign * yAbankPDFParser.parse_amount(fields['amount'])
                amount_local = fields['amount']
                currency = 'NOK'
                date = '%i-%i-%i' % (yAbankPDFParser.YYYY, int(mm), int(dd))
                yield date, account, amount, amount_local, currency

                page_pos = entry.end()
                get_entry()

            page_pos = 0


    @staticmethod
    def post_process(db, bogus=None):
        if bogus:
            # Remove the last entry, the invoice sum
            db.remove(bogus)
            INFO('  removed invoice sum entry')


class CSVParser(Parser):

    @classmethod
    def read_file(cls, fpath):
        data = super().read_file(fpath)
        data = data.decode(cls.CHARSET)
        return data.split('\n')[cls.SKIP:]
        
    @classmethod
    def parse(cls, fpath):
        entry = {}
        for line in cls.read_file(fpath):
            if not line:
                continue
            line = [cell.strip('"') for cell in line.split(cls.DELIM)]
            date = datetime.strptime(line[cls.DATEIDX], cls.DATEFORMAT).date().isoformat()
            account = line[cls.ACCTIDX]
            amount = amount_local = cls.parse_amount(line[cls.AMOUNTIDX])
            currency = line[cls.CURRENCYIDX]
            if cls.AMOUNTLCIDX != cls.AMOUNTIDX:
                amount_local = cls.parse_amount(line[cls.AMOUNTLCIDX])
            account, amount, currency = cls._parse(account, amount, currency)
            yield date, account, amount, amount_local, currency

    @staticmethod
    def _parse(cls, *args):
        return args


class yAbankCSVParser(CSVParser):

    CHARSET       = 'utf-8'#'iso-8859-10'
    DATEFORMAT    = '%d.%m.%Y'
    DELIM         = ';'
    SKIP          = 0

    RE_NONLOCAL   = re.compile(r"^VISA .+ \d\d.\d\d (\D+) (\d+,\d\d) .+$")
    DATEIDX       = 1
    ACCTIDX       = 2
    AMOUNTIDX     = 3
    CURRENCYIDX   = -1
    AMOUNTLCIDX   = AMOUNTIDX

    @classmethod
    def _parse(cls, account, amount, currency):
        # Special actions
        try:
            currency, amount = cls.RE_NONLOCAL.match(account).groups()
            amount = cls.parse_amount(amount)
        except AttributeError:
            currency = 'NOK'
        return account, amount, currency


class BankNorwegianCSVParser(CSVParser):

    CHARSET       = 'utf-8'
    DATEFORMAT    = '%m/%d/%Y'
    DELIM         = ';'
    SKIP          = 1

    DATEIDX       = 0
    ACCTIDX       = 1
    AMOUNTIDX     = 3
    CURRENCYIDX   = 5
    AMOUNTLCIDX   = 6


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
    def parse(cls, fpath):
        import xlrd
        entry = {}
        datemode, rows = cls.read_file(fpath)
        for row in rows:
            date = xlrd.xldate_as_datetime(row[cls.DATEIDX].value, datemode).isoformat()
            account = row[cls.ACCTIDX].value
            amount = amount_local = row[cls.AMOUNTIDX].value
            currency = row[cls.CURRENCYIDX].value
            if cls.AMOUNTLCIDX != cls.AMOUNTIDX:
                amount_local = row[cls.AMOUNTLCIDX].value
            yield date, account, amount, amount_local, currency


class BankNorwegianXLSParser(XLSParser):

    CHARSET       = 'utf-8'
    SHEET         = 'transactions'

    DATEIDX       = 0
    ACCTIDX       = 1
    AMOUNTIDX     = 3
    CURRENCYIDX   = 5
    AMOUNTLCIDX   = 6
