import re, os, datetime
from HTMLParser import HTMLParser
from hashlib import md5
from transaction import Transaction

class __Parser__(object):

    @classmethod
    def update(cls, files_md5, stats):
        updated = False
        for f in os.listdir(cls.__dir__):
            try:
                if os.path.splitext(f)[1] != cls.__fext__:
                    continue
                f = cls.__dir__ + f
                data = open(f, 'rb').read()
                _md5 = md5(data).hexdigest()
                if not files_md5.has_key(f) or files_md5[f] != _md5:
                    stats.update(cls.parse(data))
                    files_md5[f] = _md5
                    updated = True
                    print "Successfully parsed", f
            except IOError: 
                print "Could not open file", f
            except BaseException as e:
                print "Exception", f + ':\n', e.message
        return updated
            
class yAbankParser(__Parser__, object):

    CHARSET = 'iso-8859-10'
    __fext__ = '.csv'
    __dir__ = './yabank/'

    @staticmethod
    def parse(data):
        data = data.decode(yAbankParser.CHARSET).encode('utf-8')
        transactions = {}
        for line in data.split('\n'):
            if not line:
                continue
            line = line.split(';')
            date = line[1]
            account = line[2]
            amount_local = amount = line[3]
            currency = 'NOK'
            non_local = \
                re.match("VISA .+ \d\d.\d\d (\D+) (\d+,\d\d) .+", account)
            if non_local:
                currency, amount = non_local.groups()
            tr = Transaction()
            tr.set_account(account)
            tr.set_amount(amount)
            tr.set_amount_local(amount_local)
            tr.set_currency(currency)
            dd, mm, yyyy = date.split('-')
            tr.set_date(datetime.date(int(yyyy), int(mm), int(dd)))
            transactions[md5(str(tr)).hexdigest()] = tr
        return transactions


class BankNorwegianPDFParser(__Parser__, HTMLParser, object):

    CHARSET = 'iso-8859-1'
    __fext__ = '.pdf'
    __dir__ = './banknorwegian/'
    __re__ = re.compile(r'^(?P<date>\d\d\.\d\d\.\d{4,4})' \
                        '(?P<account>.+)\d{6,6}\*{6,6}\d{4,4}' \
                        '(?P<amount>\d+,\d+)' \
                        '(?P<currency>[A-Z]+)(\d\.\d{4,4})?' \
                        '(?P<amount_local>\d+,\d+)$')

    def __init__(self):
        self.is_tr = False
        super(BankNorwegianPDFParser, self).__init__()
        self.transactions = {}

    @staticmethod
    def parse(data):
        inst = BankNorwegianPDFParser()
        inst.feed(inst.convert(data))
        return inst.transactions

    @staticmethod
    def convert(data):
        from pdfminer.pdfinterp import PDFResourceManager, process_pdf
        from pdfminer.converter import HTMLConverter
        from StringIO import StringIO
        pdfdata = StringIO(data)
        htmldata = StringIO()
        man = PDFResourceManager()
        conv = HTMLConverter(man, htmldata)
        process_pdf(man, conv, pdfdata)
        data = htmldata.seek(0) or htmldata.read()
        return data

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            self.is_tr = False

    def handle_endtag(self, tag):
        if tag == "span":
            self.is_tr = True

    def handle_data(self, data):
        if self.is_tr:
            data = data.strip()
            if not data:
                return
            match = self.__re__.match(data)
            if match:
                gr = match.groupdict()
                tr = Transaction()
                tr.set_account(gr["account"])
                tr.set_amount(gr["amount"],-1)
                tr.set_amount_local(gr["amount_local"],-1)
                tr.set_currency(gr["currency"])
                dd, mm, yyyy = gr["date"].split('.')
                tr.set_date(datetime.date(int(yyyy), int(mm), int(dd)))
                self.transactions[md5(str(tr)).hexdigest()] = tr


class BankNorwegianHTMLParser(__Parser__, HTMLParser, object):

    CHARSET = 'iso-8859-1'
    __fext__ = '.html'
    __dir__ = './banknorwegian/'

    def __init__(self):

        self.DATE        =   1
        self.ACCOUNT     =   2
        self.AMOUNT      =   8
        self.CURRENCY    =  16
        self.AMOUNTLOCAL =  64
        self.RETURN      = 128

        super(BankNorwegianHTMLParser, self).__init__()
        self.is_trtable = False
        self.is_tr = False
        self.tr = None
        self.next = 0
        self.transactions = {}

    @staticmethod
    def parse(data):
        inst = BankNorwegianHTMLParser()
        inst.feed(data)
        return inst.transactions

    def handle_starttag(self, tag, attrs):
        if self.is_trtable and tag == 'td':
            self.is_tr = True
        # Start of transaction
        if self.is_trtable and tag == 'tr':
            self.tr = Transaction()
            self.next = 1
        # Flight table ...
        elif tag == 'br' and self.next:
            self.is_trtable = False
        # Start of a transaction table
        elif tag == 'table' and attrs == [('class','transTable')]:
            self.is_trtable = True

    def handle_endtag(self, tag):
        # End of transaction data
        if tag == 'td' and self.is_trtable:
            self.is_tr = False
            self.next = self.next << 1         
        # End of transaction
        elif  tag == 'tr' and self.is_trtable and self.next & self.RETURN:
            self.transactions[md5(str(self.tr)).hexdigest()] = self.tr
            self.tr = None
            self.is_tr = False
            self.next = 0
        # End of table
        elif tag == 'table':
            # Flight table ...
            if self.next:
                self.is_trtable = True
                self.next |= self.RETURN
            else:
                self.is_trtable = False

    def handle_data(self, data):
        if self.is_trtable and self.is_tr:
            if self.next & self.RETURN:
                self.next ^= self.RETURN
                return
            
            data = data.decode(self.CHARSET).encode('utf-8')
            data = re.sub(r'\s+', '', data)

            # Set date
            if self.next & self.DATE:
                dd, mm, yyyy = data.split('.')
                self.tr.set_date(datetime.date(int(yyyy), int(mm), int(dd)))
            # Set account
            elif self.next & self.ACCOUNT:
                self.tr.set_account(data)
            # Set amount
            elif self.next & self.AMOUNT:
                self.tr.set_amount(data,-1)
            # Set currency
            elif self.next & self.CURRENCY:
                self.tr.set_currency(data)
            # Set amount in local currency
            elif self.next & self.AMOUNTLOCAL:
                self.tr.set_amount_local(data,-1)


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
                    print "Failed to parse:", line
                    continue
            elif line[0:17] == "B   30 SIGN.ANNUL":
                del tickets[this]
            elif line[0:2] == " <":
                this = None
        return tickets

