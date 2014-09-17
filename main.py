#!/usr/bin/env python

import os, sys, pickle, traceback, curses
from curses import panel
from hashlib import md5
from parse import yAbankParser, BankNorwegianParser
from stats import Stats, Year, Month
from config import configure
import ui
from ui import Dict, Menu


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
    if os.path.splitext(f)[1] != '.html':
        continue
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
    if os.path.splitext(f)[1] != '.csv':
        continue
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

labels, settings = configure()
#stats = Stats(transactions, labels, settings)
obj = Month(2014,8,transactions=transactions,labels=labels,
            settings=settings)


if updated:
    pickle.dump(files_md5, open(f_pickle, 'w'))
    pickle.dump(transactions, open(t_pickle, 'w'))


def main_loop(menus, stdscr, win):
    visible = None
    while 1:
        c = stdscr.getch()
        # ignore everything that is not a letter
        if c > 122 or c < 65:
            continue
        # letter
        c = chr(c).lower()
        # display a menu
        if menus[c]:
            # hide open menu
            if visible:
                menus[visible].hide()
                if visible == c:
                    visible = None
                    continue
            # show menu
            menus[c].show()
            visible = c
            continue
        # menu is open -> do action
        if visible and menus[visible][c]:
            continue
        if c == "a":
            y = 1
            for line in str(obj).split('\n'):
                win.addstr(y, 1, line)
                y += 1
            win.refresh(0,0,2,1,20,70)
        # exit
        if c == "e":
            return


if __name__ == "__main__":
    try:
        WIDTH = 80
        HEIGHT = 24
        MENU0 = 2
        MENUW = 10

        stdscr = ui.init(HEIGHT, WIDTH)
        stdscr.hline(2, 1, curses.ACS_HLINE, WIDTH - 2)
        main_win = curses.newpad(1000, WIDTH)
        main_win.refresh(0,0,3,3,6,6)
        #main_panel = curses.panel.new_panel(main_win)
        main_win.border(0)

        menus = Dict()
        menus["f"] = Menu.add_menu(stdscr, "File" , MENU0, MENUW,
                                   (("Load"  ,None),
                                    ("Update",None)))
        menus["p"] = Menu.add_menu(stdscr, "Plot" , MENU0 + MENUW, MENUW,
                                   (("Month" ,None),
                                    ("Year"  ,None),
                                    ("Total" ,None)))
        menus["s"] = Menu.add_menu(stdscr, "Stats", MENU0 + 2*MENUW, MENUW,
                                   (("Month" ,None),
                                    ("Year"  ,None),
                                    ("Total" ,None)))
        Menu.add_menu(stdscr, "Exit", MENU0 + 3*MENUW, MENUW)

        main_loop(menus, stdscr, main_win)
    except:
        ui.clean_up(stdscr)
        print traceback.format_exc()
    else:
        ui.clean_up(stdscr)








# def main(stdscr):
#     while 1:
#         c = stdscr.getch()

# if __name__ == "__main__":
#     try:
#         # Initialize curses
#         stdscr = curses.initscr()
#         # Turn off echoing of keys, and enter cbreak mode,
#         # where no buffering is performed on keyboard input
#         curses.noecho()
#         curses.cbreak()

#         # In keypad mode, escape sequences for special keys
#         # (like the cursor keys) will be interpreted and
#         # a special value like curses.KEY_LEFT will be returned
#         stdscr.keypad(1)
#         main(stdscr)                    # Enter the main loop
#     except:
#         pass
#     finally:
#         # Restore terminal to sane state
#         stdscr.keypad(0)
#         curses.echo()
#         curses.nocbreak()
#         curses.endwin()


