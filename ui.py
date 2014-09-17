import curses, sys, traceback
from curses import panel

class Dict(dict):
    """
    This is the Same as :py:obj:`dict`, but it returns ``False`` instead \
    of raising :py:exc:`~exceptions.KeyError` whenever a non-existing object \
    is requested.
    """
    def __getitem__(self, key):
        if self.has_key(key):
            return super(Dict, self).__getitem__(key)
        return False

class Menu():
    """
    Class for holding the window, panel and a dictionary of actions
    for a menu. The menu object can be used as a dicitionary to
    set or request actions.

    ``menu = Menu(window_inst)`` \n
    ``menu['a'] = [banankake, 3]``
    
    The function named banankake that takes an :py:obj:`int` as \
    argument will be run if 'a' is requested from menu.

    ``banankake_return = menu['a']``

    :param win: menu window
    :type win: :py:obj:`curses.window` 
    """
    def __init__(self, win):
        self.window = win
        self.panel = curses.panel.new_panel(win)
        self.panel.hide()
        panel.update_panels()
        self.actions = Dict()
    def show(self):
        """
        Hide the menu panel by calling :py:meth:`curses.panel.Panel.hide()`.
        """
        self.panel.show()
        panel.update_panels()
        self.window.refresh()
    def hide(self):
        """
        Hide the menu panel by calling :py:meth:`curses.panel.Panel.hide()`.
        """
        self.panel.hide()
        self.window.refresh()
    def __getitem__(self, key):
        action = self.actions[key]
        if action:
            func = action[0]
            args = action[1:]
            func(*args)
            panel.update_panels()
    def __setitem__(self, key, action):
        assert(type(action) == list)
        self.actions[key] = action

    @staticmethod
    def add_menu(win, title, xpos, width, items = None):
        """
        Add a menu to the input window. \
        Items in the menu are specified in ``items``.

        :param win: window
        :type win: :py:obj:`curses.window` 
        :param str title: title of menu
        :param int xpos: position
        :param int width: width of menu
        :param items: menu items and actions
        :type items: :py:obj:`tuple` ( :py:obj:`tuple` ( :py:obj:`str` , \
        :py:obj:`list` [ `function` , `*args` ] ) , ... )
        """
        HEIGH, WIDTH = win.getmaxyx()
        assert((type(title) == str) and len(title))
        assert((type(xpos) == int) and xpos >= 0 and xpos <= WIDTH)
        win.addstr(1, xpos, title[0], curses.A_BOLD)
        win.addstr(1, xpos+1, title[1:])
        n = len(items) if items else 0
        menu = None
        if n:
            win = curses.newwin(n+2, width, 2, xpos)
            win.border(0)
            i = 0
            for (name, action) in items:
                win.addstr(1+i, 1, name[0], curses.A_BOLD)
                win.addstr(1+i, 2, name[1:])
                i += 1
            menu = Menu(win)
            if action:
                menu[name[0].lower()] = [action]
        curses.doupdate()
        return menu

        
def init(h, w):
    # Initialize curses
    stdscr = curses.initscr()
    stdscr.resize(h, w)
    stdscr.border(0)
    # Turn off echoing of keys, and enter cbreak mode,
    # where no buffering is performed on keyboard input
    curses.noecho()
    curses.cbreak()
    # In keypad mode, escape sequences for special keys
    # (like the cursor keys) will be interpreted and
    # a special value like curses.KEY_LEFT will be returned
    stdscr.keypad(1)
    return stdscr


def clean_up(stdscr):
    """
    Restore terminal to sane state.

    :param stdscr: main window
    :type stdscr: :py:obj:`curses.window` 
    """
    stdscr.keypad(0)
    curses.nocbreak()
    curses.endwin()
    curses.echo()
