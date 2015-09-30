#!/usr/bin/env python

import os, sys
from argparse import ArgumentParser
from banan import TransactionsDB, Config
from banan import yAbankCSVParser, yAbankPDFParser, BankNorwegianCSVParser


map_of_maps = {

    'yabank'        : { '.csv' : yAbankCSVParser,
                        '.pdf' : yAbankPDFParser },

    'banknorwegian' : { '.csv' : BankNorwegianCSVParser }

} 


def main(args):
    
    if not args.fpath and not args.server_action:
        parser.print_help()
        exit(0)

    if args.server_action:
        # todo
        print args.server_action, 'server'

    if args.fpath:
        ext = os.path.splitext(args.fpath)[1]
        bankparser = None
        try:
            assert(ext)
            if not args.bank: raise AttributeError
            bankparser = map_of_maps[args.bank][ext]
        except AttributeError:
            print('ERROR: option -f requires option -b')
            exit(0)
        except AssertionError:
            print('ERROR: FILE must end with file extension, e.g. \'.csv\'')
            exit(0)
        except KeyError:
            print('ERROR: no known %s %s parser' % (args.bank, ext))
            exit(0)

        conf = Config()
        db = TransactionsDB(conf)
        
        try:
            db.feed(args.fpath, bankparser, args.skip_duplicates, args.overwrite_duplicates, args.dry_run)
        except SystemExit:
            print('SystemExit raised')
            exit(0)
        finally:
            print('Closing database ...')
            db.close()


def parse_args():

    usage = '%s start | restart | stop | -f -b [-s|-o|--dry] | -h' % sys.argv[0]
    desc = 'Feed bank statement to buzhug database or manage server'
    parser = ArgumentParser(usage=usage, description=desc)

    db_group = parser.add_argument_group('# Database feed')
    db_group.add_argument('-f', '--feed', dest='fpath', metavar='FILE', help='feed FILE to buzhug')
    db_group.add_argument('-b', '--bank', dest='bank', metavar='BANK', help='origin of FILE')

    db_opts = parser.add_argument_group('  options')
    db_opts.add_argument('-s', '--skip-dup', dest='skip_duplicates',
                         const=False, default=True, action='store_const',
                         help='do not check for duplicates in buzhug')
    db_opts.add_argument('-o', '--overwrite', dest='overwrite_duplicates',
                         const=True, default=False, action='store_const',
                         help='overwrite duplicates in buzhug (overrides -s)')
    db_opts.add_argument('--dry', dest='dry_run', 
                         const=True, default=False, action='store_const',
                         help='dry run: only print parsed transactions to console')

    server_group = parser.add_argument_group('# Server management')
    server_group.add_argument(dest='server_action', choices=('start','restart','stop'),
                              help='start, restart or stop server')

    return parser.parse_args(sys.argv[1:])


if __name__ == '__main__':
    args = parse_args()
    main(args)


            
exit(0)

import os
from banan import TransactionsDB, Config
from banan import yAbankCSVParser, yAbankPDFParser, BankNorwegianCSVParser
conf = Config()
db = TransactionsDB(conf)
dup = False
for f in os.listdir('yabank'):
    fpath = 'yabank/' + f
    if f[-4:] == '.csv':
        db.feed(fpath, yAbankCSVParser, dup)
    if f[-4:] == '.pdf':
        fpath = 'yabank/' + f
        db.feed(fpath, yAbankPDFParser, dup)
for f in os.listdir('banknorwegian'):
    fpath = 'banknorwegian/' + f
    if f[-4:] == '.csv':
        db.feed(fpath, BankNorwegianCSVParser, dup)
db.close()

