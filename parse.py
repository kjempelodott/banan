# -*- coding: utf-8 -*-
import re, os
from logger import *
from datetime import date, datetime
    

class Parser(object):

    RE_NO = re.compile(r'(^-?[\.\d]+?)([,\.](\d{1,2}))?$')
    
    @classmethod
    def read_file(cls, fpath):
        INFO('[%s] %s' % (cls.__name__, fpath))
        try:
            ext = os.path.splitext(fpath)[1]
            if ext != cls.FILEEXT:
                ERROR('[%s] can not parse %s' % (cls.__name__, ext))
                return

            data = open(fpath, 'rb').read()
            return data

        except IOError: 
            ERROR('[%s] could not be opened for reading ' % fpath)

    @staticmethod
    def parse_amount(value, sign = 1):
        _value = value.replace(' ', '')
        try:
            m = Parser.RE_NO.match(_value).groups()
            _value = m[0].replace('.','') + '.' + (m[2] if m[2] else '00')
            return sign * float(_value)
        except:
            ERROR('failed to parse amount ' + value)

    @staticmethod
    def post_process(db, **kw):
        pass


class yAbankPDFParser(Parser):

    FILEEXT   = '.pdf'

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

                fields['amount']       = sign * yAbankPDFParser.parse_amount(fields['amount'])
                fields['amount_local'] = fields['amount']
                fields['currency']     = 'NOK'
                fields['date']         = date(yAbankPDFParser.YYYY, int(mm), int(dd))

                yield fields

                page_pos = entry.end()
                get_entry()

            page_pos = 0


    @staticmethod
    def post_process(db, offset):
        if db._pos.next_id > offset:
            # Remove the last entry, the invoice sum
            db.delete(db[db._pos.next_id - 1])

          
class CSVParser(Parser):

    @classmethod
    def parse(cls, fpath):
        data = cls.read_file(fpath)
        data = data.decode(cls.CHARSET).encode('utf-8')
        
        entry = {}
        for line in data.split('\n')[cls.SKIP:]:

            if not line:
                continue
            line = line.split(cls.DELIM)

            entry['date']         = datetime.strptime(line[cls.DATEIDX], cls.DATEFORMAT).date()
            entry['account']      = line[cls.ACCTIDX]
            entry['amount']       = CSVParser.parse_amount(line[cls.AMOUNTIDX])
            entry['amount_local'] = CSVParser.parse_amount(line[cls.AMOUNTLCIDX]) if \
                                    cls.AMOUNTLCIDX != cls.AMOUNTIDX else entry['amount']
            entry['currency']     = line[cls.CURRENCYIDX]
            cls._parse(entry)

            yield entry

    @classmethod
    def _parse(cls, entry):
        pass

  
class yAbankCSVParser(CSVParser):

    CHARSET       = 'iso-8859-10'
    FILEEXT       = '.csv'
    DATEFORMAT    = '%d-%m-%Y'
    DELIM         = ';'
    SKIP          = 0

    RE_NONLOCAL   = re.compile(r"^VISA .+ \d\d.\d\d (\D+) (\d+,\d\d) .+$")
    DATEIDX       = 1
    ACCTIDX       = 2
    AMOUNTIDX     = 3
    CURRENCYIDX   = -1
    AMOUNTLCIDX   = AMOUNTIDX

    @staticmethod
    def _parse(entry):
        try:
            entry['currency'], entry['amount'] = \
                yAbankCSVParser._RE_NONLOCAL.match(account).groups()
        except:
            entry['currency'] = 'NOK'


class BankNorwegianCSVParser(CSVParser):

    CHARSET       = 'utf-8'
    FILEEXT       = '.csv'
    DATEFORMAT    = '%m/%d/%Y'
    DELIM         = ';'
    SKIP          = 1

    DATEIDX       = 0
    ACCTIDX       = 1
    AMOUNTIDX     = 3
    CURRENCYIDX   = 5
    AMOUNTLCIDX   = 6

