import curses, sys, traceback
from curses import panel

class panel_map(dict):
    def __getitem__(self, key):
        if self.has_key(key):
            return super(panel_map, self).__getitem__(key)
        return False


MENUW = 10
X0, Y0 = (2, 1)
h, w = (0, 0)
stdscr = None
visible = None
panels = panel_map()


def main():
    global visible
    while 1:
        stdscr.refresh()
        c = chr(stdscr.getch()).lower()
        stdscr.addstr(10, 10, c)
        if panels[c]:
            if visible:
                panels[visible].hide()
                if visible == c:
                    visible = None
                    continue
            panels[c].show()
            visible = c
            panel.update_panels()
            continue
        if c == "e":
            return
        

def init():
    global h, w, stdscr, visible, panels
    # Initialize curses
    stdscr = curses.initscr()
    stdscr.border(0)
    # Turn off echoing of keys, and enter cbreak mode,
    # where no buffering is performed on keyboard input
    curses.noecho()
    curses.cbreak()
    # In keypad mode, escape sequences for special keys
    # (like the cursor keys) will be interpreted and
    # a special value like curses.KEY_LEFT will be returned
    stdscr.keypad(1)

    # No menu panels visible
    visible = None

    h, w = stdscr.getmaxyx()
    panels["f"] = add_menu_item("File" , X0,             ("Load", "Update"))
    panels["p"] = add_menu_item("Plot" , X0 + MENUW,   ("Month", "Year", "Total"))
    panels["s"] = add_menu_item("Stats", X0 + 2*MENUW, ("Month", "Year", "Total"))

    add_menu_item("Exit", X0 + 3*MENUW)
    stdscr.hline(X0, Y0, curses.ACS_HLINE, w - X0)

    return stdscr


def add_menu_item(title, xpos, items = None):
    assert((type(title) == str) and len(title))
    assert((type(xpos) == int) and xpos >= 0 and xpos <= w)
    stdscr.addstr(Y0, xpos, title[0], curses.A_BOLD)
    stdscr.addstr(Y0, xpos+1, title[1:])
    n = len(items) if items else 0
    menu = None
    if n:
        menu_win = curses.newwin(n+2, MENUW, Y0+1, xpos)
        menu_win.border(0)
        i = 0
        for it in items:
            menu_win.addstr(Y0+i, 1, it[0], curses.A_BOLD)
            menu_win.addstr(Y0+i, 2, it[1:])
            i += 1
        menu = curses.panel.new_panel(menu_win)
        menu.hide()
        panel.update_panels()
    curses.doupdate()
    return menu


def clean_up():
    # Restore terminal to sane state
    stdscr.keypad(0)
    curses.nocbreak()
    curses.endwin()
    curses.echo()


if __name__ == "__main__":
    try:
        init()
        main()
    except:
        clean_up()
        print traceback.format_exc()
    else:
        clean_up()
