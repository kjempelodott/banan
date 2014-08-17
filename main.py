#!/usr/bin/env python

import os, pickle
from hashlib import md5
from parse import yAbankParser, BankNorwegianParser
from stats import Stats
from config import configure_groups

files_md5 = {}
f_pickle = './.files_md5.pickle'
#if os.path.exists(f_pickle):
#    files_md5 = pickle.loads(open(f_pickle, 'r').read())

transactions = {}
t_pickle = './.transactions.pickle'
#if os.path.exists(t_pickle):
#    transactions = pickle.loads(open(t_pickle, 'r').read())

updated = False

for f in os.listdir('./banknorwegian'):
    try:
        f = './banknorwegian/' + f
        data = open(f, 'r').read()
        _md5 = md5(data).hexdigest()
        if files_md5.has_key(f) and files_md5[f] == _md5:
            print "Skipping", f
            continue # Already parsed, no changes
        else:
            parser = BankNorwegianParser()
            parser.feed(data)
            transactions.update(parser.transactions)
            files_md5[f] = _md5
            updated = True
            print "Successfully parsed", f            
    except IOError:
        print "Could not open file", f
    except:
        print "Failed to parse", f


for f in os.listdir('./yabank'):
    try:
        f = './yabank/' + f
        data = open(f, 'r').read()
        _md5 = md5(data).hexdigest()
        if files_md5.has_key(f) and files_md5[f] == _md5:
            print "Skipping", f
            continue # Already parsed, no changes
        else:
            parser = yAbankParser()
            parser.parse(data)
            transactions.update(parser.transactions)
            files_md5[f] = _md5
            updated = True
            print "Successfully parsed", f
    except IOError:
        print "Could not open file", f
    except:
        print "Failed to parse", f

conf = configure_groups()
stats = Stats(transactions, conf)

if updated:
    pickle.dump(files_md5, open(f_pickle, 'w'))
    pickle.dump(transactions, open(t_pickle, 'w'))

for v in sorted(transactions.values()):
    print v


# import curses, traceback

# if __name__ == "__main__":
#     try:
#         # Initialize curses
#         stdscr=curses.initscr()
#         # Turn off echoing of keys, and enter cbreak mode,
#         # where no buffering is performed on keyboard input
#         curses.noecho()
#         curses.cbreak()
        
#         # In keypad mode, escape sequences for special keys
#         # (like the cursor keys) will be interpreted and
#         # a special value like curses.KEY_LEFT will be returned
#         stdscr.keypad(1)
#         main(stdscr)                    # Enter the main loop
#         # Set everything back to normal
#         stdscr.keypad(0)
#         curses.echo()
#         curses.nocbreak()
#         curses.endwin()                 # Terminate curses
#     except:
#         # In event of error, restore terminal to sane state.
#         stdscr.keypad(0)
#         curses.echo()
#         curses.nocbreak()
#         curses.endwin()
#         traceback.print_exc()           # Print the exception
