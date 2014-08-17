import re, datetime
from HTMLParser import HTMLParser
from hashlib import md5
from transaction import Transaction

class yAbankParser(object):

    def __init__(self):
        self.transactions = {}

    def parse(self, data):
        for line in data.split('\n'):
            if not line:
                continue
            line = line.split(';')
            date = line[1]
            account = line[2]
            amount_local = amount = line[3]
            currency = 'NOK'
            non_local = re.match("VISA .+ \d\d.\d\d (\D+) (\d+,\d\d) .+", account)
            if non_local:
                currency, amount = non_local.groups()
            tr = Transaction()
            tr.set_account(account)
            tr.set_amount(amount)
            tr.set_amount_local(amount_local)
            tr.set_currency(currency)
            dd, mm, yyyy = date.split('-')
            tr.set_date(datetime.date(int(yyyy), int(mm), int(dd)))
            self.transactions[md5(str(tr)).hexdigest()] = tr


class BankNorwegianParser(HTMLParser, object):

    def __init__(self):
        self.DATE        =   1
        self.ACCOUNT     =   2
        self.AMOUNT      =   8
        self.CURRENCY    =  16
        self.AMOUNTLOCAL =  64
        self.RETURN      = 128

        super(BankNorwegianParser, self).__init__()
        self.is_trtable = False
        self.is_tr = False
        self.tr = None
        self.next = 0
        self.transactions = {}

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