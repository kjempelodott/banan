#!/usr/bin/env python

from banan import TransactionsDB, Config
from banan import yAbankCSVParser, yAbankPDFParser, BankNorwegianCSVParser

c = Config()
t = TransactionsDB(c)
t.clearall()
dup = False

import os

for f in os.listdir('yabank'):
    fpath = 'yabank/' + f
    if f[-4:] == '.csv':
        t.feed(fpath, yAbankCSVParser, dup)
    if f[-4:] == '.pdf':
        fpath = 'yabank/' + f
        t.feed(fpath, yAbankPDFParser, dup)
for f in os.listdir('banknorwegian'):
    fpath = 'banknorwegian/' + f
    if f[-4:] == '.csv':
        t.feed(fpath, BankNorwegianCSVParser, dup)


t.db.close()

