#!/usr/bin/env python

import os, sys, pickle, traceback, curses
from curses import panel
from hashlib import md5

from config import configure
import ui
from ui import Dict, Menu, Prompt
from parse import *
from stats import *

LOG = open("debug.log", "w")
FUCK_CURSES = True

class Banan:

    def __init__(self):
        self._CONF = './labels.conf'
        self._FILES = './.files.pickle'
        self._STATS = './.stats.pickle'
        self._year = self._month = None
        self.labels, self.settings = configure(self._CONF)
        self.load()
        self.cat_pad = None
        self.cat_coord = ()

    def load(self):
        self._files = {}
        if os.path.exists(self._FILES):
            self._files = pickle.loads(open(self._FILES, 'r').read())

            if os.path.exists(self._STATS):
                self._stats = self.stats = pickle.loads(open(self._STATS, 'r').read())
                return

        # Something is wrong, reset everything
        for f in (self._FILES, self._STATS):
            try:
                os.remove(f)
            except: 
                pass

        self._files = {}
        self._stats = self.stats = Stats(labels = self.labels,
                                         settings = self.settings,
                                         transactions = {})
        self.update()
    
    def update(self):
        with open(self._CONF, 'r') as conf:
            _md5 = md5(conf.read()).hexdigest()
            if not self._CONF in self._files or self._files[self._CONF] != _md5:
                # Config has changed, replace labels
                self._files[self._CONF] = _md5
                self.labels, self.settings = configure(self._CONF)
                self._stats.assign_labels(labels = self.labels, settings = self.settings)

        classes = [BankNorwegianCSVParser, yAbankCSVParser, yAbankPDFParser]
        for cls in classes:
            cls.update(self._files, self._stats)

    def save(self):
        pickle.dump(self._files, open(self._FILES, 'w'))
        pickle.dump(self._stats, open(self._STATS, 'w'))

    def print_cats(self):
        try:
            y = 1
            for l in sorted(self.labels):
                self.cat_pad.addstr(y, 1, l)
                y += 1
            self.cat_pad.refresh(*self.cat_coord)
        except:
            ERROR('print_cats() in Banan called before set_cat_pad()')
            raise Exception

    def set_cat_pad(self, pad, HEIGHT):
        self.cat_coord = (0, 0,  2, 1,  HEIGHT-2, pad.getmaxyx()[1])
        self.cat_pad = pad
        self.print_cats()

    def set_year(self, stdscr):
        curses.echo()
        year = int(stdscr.getstr())
        curses.noecho()
        self._year = year
        self.stats = Year(year, self._stats)

    def set_month(self, stdscr):
        curses.echo()
        month = int(stdscr.getstr())
        stdscr(addstr(14,50,'foo'))
        curses.noecho()
        self._month = month
        self.stats = Month(self._year, month, self._stats)

    
def show_help(win):
    pass
    
def main_loop(menus, stdscr, banan):
    menu_open = None
    while 1:
        c = stdscr.getch()
        # Ignore everything that is not a letter or number
        try:
            c = chr(c).lower()
            assert(c.isalnum())
        except:
            continue
        LOG.write("stdin got '%s'\n" % c)
        stdscr.addstr(14,50,c)
        if menu_open and c in menus[menu_open]:
            # Menu is open, do something
            LOG.write(" pop-up menu '%s' open\n" \
                      " -> do action '%s'\n" % (menu_open, c))
            # Do action that matches c (nothing if not match)
            menus[menu_open][c]()
            menus[menu_open].hide()
            # Re-print categories ...
            banan.print_cats()
            menu_open = None
        elif menus[c]:
            # Open or hide menu
            LOG.write(" open menu '%s'\n" % c)
            if menu_open:
                # Hide open menu
                LOG.write(" hide menu '%s'\n" % menu_open)
                menus[menu_open].hide()
                banan.print_cats()
                if menu_open == c:
                    menu_open = None
                    continue
            # Try to open new menu
            result = menus[c].show()
            if not result:
                LOG.write(" -> not a pop-up menu, doing action '%s'\n" 
                          "    %s\n" % (c, str(menus[c][c])))
                # Not a menu or a prompt, do something
                menus[c][c]()
                continue
            if type(result) is str:
                pass
            else:
                # It was a pop-up menu!
                menu_open = c


if __name__ == '__main__':
    if FUCK_CURSES:
 
        banan = Banan()
        banan.update()
        banan.save()
        print Month(2015, 8, banan._stats)
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

        menus['f'] = Menu.add_menu(stdscr, 'File' , MENU0, MENUW,
                                   (('Update',banan.update),
                                    ('Save',banan.save)))
        menus['p'] = Menu.add_menu(stdscr, 'Plot' , MENU0 + MENUW, MENUW,
                                   (('Data',    None),
                                    ('Average', None)))

        menus['m'] = Prompt.add_menu(stdscr, 'Month', MENU0 + 2*MENUW, MENUW, [banan.set_month, stdscr])
        menus['y'] = Prompt.add_menu(stdscr, 'Year', MENU0 + 3*MENUW, MENUW, [banan.set_year, stdscr])
        # Menu.add_menu(stdscr, 'Help', MENU0 + 4*MENUW, MENUW,
        #               [show_help, stdscr])
        menus['e'] = Menu.add_menu(stdscr, 'Exit', MENU0 + 5*MENUW, MENUW, [ui.clean_up, stdscr])

        banan.set_cat_pad(cat_pad, HEIGHT)
        main_loop(menus, stdscr, banan)
    except Exception:
        ui.clean_up(stdscr, False)
        print traceback.format_exc()
    else:
        ui.clean_up(stdscr)
    finally:
        ui.clean_up(stdscr)
        print banan.stats
        LOG.close()
