import curses, sys
from curses import panel

def main():
    while 1:
        c = stdscr.getch()
        if c in [ord('e'), ord('E')]:
            return

def init():
    global HEIGHT, WIDTH, stdscr
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

    HEIGHT, WIDTH = stdscr.getmaxyx()

    add_menu_item("File",  2, ("Load", "Update"))
    add_menu_item("Plot",  8, ("Month", "Year", "Total"))
    add_menu_item("Stats",14, ("Month", "Year", "Total"))
    add_menu_item("Exit", 21)
    stdscr.hline(2, 1, curses.ACS_HLINE, WIDTH - 2)

    return stdscr

def add_menu_item(title, xpos, items = None):
    assert((type(title) == str) and len(title))
    assert((type(xpos) == int) and xpos >= 0 and xpos <= WIDTH)
    stdscr.addstr(1, xpos, title[0], curses.A_BOLD)
    stdscr.addstr(1, xpos+1, title[1:])
    menu = curses.panel.new_panel(curses.newwin(4, 6, 1, xpos))
    menu.hide()
    panel.update_panels()
    curses.doupdate()

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
    except Exception as e:
        clean_up()
        print "Error:", e.message
    except:
        clean_up()
    else:
        clean_up()
