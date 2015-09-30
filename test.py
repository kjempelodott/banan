#!/usr/bin/env python

from db import db
import parse
import config

c = config.Config()
t = db.TransactionsDB(c)
t.clearall()
dup = False

import os

for f in os.listdir('yabank'):
    fpath = 'yabank/' + f
    if f[-4:] == '.csv':
        t.feed(fpath, parse.yAbankCSVParser, dup)
    if f[-4:] == '.pdf':
        fpath = 'yabank/' + f
        t.feed(fpath, parse.yAbankPDFParser, dup)
for f in os.listdir('banknorwegian'):
    fpath = 'banknorwegian/' + f
    if f[-4:] == '.csv':
        t.feed(fpath, parse.BankNorwegianCSVParser, dup)


t.db.close()

