#!/usr/bin/env python

import os, sys, pickle, traceback, curses
from curses import panel
from hashlib import md5
from parse import yAbankParser, BankNorwegianParser
from stats import Stats, Year, Month
from config import configure
import ui
from ui import Dict, Menu

FUCK_CURSES=True

class Banan:

    def __init__(self):
        self.CONF = 'labels.conf'
        self.__HAS_CATS__ = False
        # labels should be saved in a pickle
        self.labels, self.settings = configure()
        self.load()
        self.cat_pad = None
        self.cat_coord = ()

    def load(self):
        self.__files__ = {}
        self.__files_pickle__ = './.files_md5.pickle'
        if os.path.exists(self.__files_pickle__):
            self.__files__ = \
                pickle.loads(open(self.__files_pickle__, 'r').read())

        self.transactions = {}
        self.__tr_pickle__ = './.transactions.pickle'
        if os.path.exists(self.__tr_pickle__):
            self.transactions = \
                pickle.loads(open(self.__tr_pickle__, 'r').read())
        
    def update(self):
        do_update = not self.__files__.has_key(self.CONF)
        if not do_update:
            with open(self.CONF, 'r') as conf:
                _md5 = md5(conf.read()).hexdigest()
                if self.__files__[self.CONF] != _md5:
                    self.__files__[self.CONF] = _md5
                    do_update = True
        do_update = \
            BankNorwegianParser.update(self.__files__, self.transactions)
        do_update |= yAbankParser.update(self.__files__, self.transactions)

        # if do_update:
        #     self.stats = Stats(self.transactions, self.labels, self.settings)
        #     self.testobj = Month(2014,8,stats=stats)

    def save(self):
        pickle.dump(self.__files__, open(self.__files_pickle__, 'w'))
        pickle.dump(self.transactions, open(self.__tr_pickle__, 'w'))

    def print_cats(self):
        try:
            y = 1
            for l in self.labels:
                self.cat_pad.addstr(y, 1, l)
                y += 1
            self.cat_pad.refresh(*self.cat_coord)
        except:
            raise Exception("print_cats() in Banan called before "
                            "set_cat_pad() has been called")

    def set_cat_pad(self, pad, HEIGHT):
        self.cat_coord = (0, 0,  2, 1,  HEIGHT-2, pad.getmaxyx()[1])
        self.cat_pad = pad
        self.print_cats()
    

def month_prompt(win):
    pass

def year_prompt(win):
    pass

def show_help(win):
    pass
    
def main_loop(menus, stdscr, b):
    menu_open = None
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
            if menu_open:
                menus[menu_open].hide()
                b.print_cats()
                if menu_open == c:
                    menu_open = None
                    continue
            # show menu
            menus[c].show()
            menu_open = c
            continue
        # menu is open -> do action
        if menu_open and menus[menu_open][c]:
            menus[menu_open][c]()
            menus[menu_open].hide()
            menu_open = None
            continue
        # exit
        if c == "e":
            return


if __name__ == "__main__":
    if FUCK_CURSES:
        banan = Banan()
        banan.update()
        banan.save()
        stats = Stats(transactions=banan.transactions, 
                      labels=banan.labels,
                      settings=banan.settings)
        testobj = Month(2014,9,stats=stats)
        print testobj
        sys.exit(0)

    try:
        WIDTH = 80
        HEIGHT = 24
        MENU0 = 2
        MENUW = 10
        MAINW = 50

        stdscr = ui.init(HEIGHT, WIDTH)
        stdscr.hline(2, 1, curses.ACS_HLINE, WIDTH - 2)

        cat_pad = curses.newpad(100, WIDTH - MAINW)
        main_pad = curses.newpad(1000, MAINW)
        cat_pad.border(0)

        banan = Banan()

        menus = Dict()
        menus["f"] = Menu.add_menu(stdscr, "File" , MENU0, MENUW,
                                   (("Update",banan.update),
                                    ("Save",banan.save)))
        menus["p"] = Menu.add_menu(stdscr, "Plot" , MENU0 + MENUW, MENUW,
                                   (("Data" ,None),
                                    ("Average"  ,None)))
        Menu.add_menu(stdscr, "Month", MENU0 + 2*MENUW, MENUW, 
                      [month_prompt, stdscr])
        Menu.add_menu(stdscr, "Year", MENU0 + 3*MENUW, MENUW, 
                      [year_prompt, stdscr])
        Menu.add_menu(stdscr, "Help", MENU0 + 4*MENUW, MENUW,
                      [show_help, stdscr])
        Menu.add_menu(stdscr, "Exit", MENU0 + 5*MENUW, MENUW, 
                      [ui.clean_up, stdscr, exit])

        b.set_cat_pad(cat_pad, HEIGHT)
        main_loop(menus, stdscr, b)
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


