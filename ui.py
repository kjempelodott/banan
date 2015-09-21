import curses, sys, traceback
from curses import panel

class Dict(dict):
    """
    A :py:obj:`dict` that returns ``False`` instead of raising 
    :py:exc:`~exceptions.KeyError` whenever a non-existing item is requested.
    """
    def __getitem__(self, key):
        if self.has_key(key):
            return super(Dict, self).__getitem__(key)
        return False

class Menu(object):
    """
    Class for holding the window, panel and a dictionary of actions
    for a menu. The menu object can be used as a dicitionary to
    set or request actions.

    ``menu = Menu(window_inst)`` \n
    ``menu['a'] = [banankake, 3]``
    
    The function named banankake that takes an :py:obj:`int` as \
    argument will be run if 'a' is requested from menu.

    ``banankake_return = menu['a']``

    :param menu_win: menu window
    :type menu_win: :py:obj:`curses.window` 
    """
    def __init__(self, menu_win, menu = True):
        self.window = None
        if menu:
            self.window = menu_win
            self.panel = curses.panel.new_panel(menu_win)
            self.panel.hide()
            panel.update_panels()
        self.actions = Dict()

    def show(self):
        """
        Hide the menu panel by calling :py:meth:`curses.panel.Panel.hide()`.
        """
        if not self.window:
            return False
        self.panel.show()
        panel.update_panels()
        curses.doupdate()
        return True

    def hide(self):
        """
        Hide the menu panel by calling :py:meth:`curses.panel.Panel.hide()`.
        """
        if not self.window:
            return
        self.panel.hide()
        panel.update_panels()
        curses.doupdate()

    def __getitem__(self, key):
        try:
            action = self.actions[key]
            func = action[0]
            args = action[1:]
            func(*args)
            #panel.update_panels()
        except Exception:
            pass

    def __contains__(self, key):
        return key in self.actions

    def __setitem__(self, key, action):
        try:
            assert(type(action) == list)
        except AssertionError: # Function without arguments
            if not action: # None cannot be called
                def _none(): pass
                action = _none
            action = [action]
        assert(str(type(action[0])) in ('<type \'function\'>',
                                        '<type \'instancemethod\'>'))
        self.actions[key] = action

    @classmethod
    def add_menu(cls, stdscr, title, xpos, width, items = None):
        """
        Add a menu to the window ``stdscr``. \
        Items in the menu are specified in ``items``.

        :param stdscr: window
        :type stdscr: :py:obj:`curses.window` 
        :param str title: title of menu
        :param int xpos: position
        :param int width: width of menu
        :param items: menu items and actions
        :type items: :py:obj:`list` or :py:obj:`tuple`

        .. note:: \
        \
        * Menu with several items \n \
                  \t ``items = ( \n \
                  \t\t ('Item1', [function1, *args]), \n \
                  \t\t ('Item2', [function2, *args]), \n \
                  \t\t ...)`` \n \
        * Menu without items \n \
                  \t ``items = [function, *args]``

        """
        HEIGHT, WIDTH = stdscr.getmaxyx()
        assert((type(title) == str) and len(title))
        assert((type(xpos) == int) and xpos >= 0 and xpos <= WIDTH)
        stdscr.addstr(1, xpos, title[0], curses.A_BOLD)
        stdscr.addstr(1, xpos+1, title[1:])
        n = len(items) if (type(items) == tuple and items) else 0
        menu = None
        if n:
            menu_win = curses.newwin(n+2, width, 2, xpos)
            menu_win.border(0)
            i = 0
            for (name, action) in items:
                menu_win.addstr(1+i, 1, name[0], curses.A_BOLD)
                menu_win.addstr(1+i, 2, name[1:])
                i += 1
            menu = Menu(menu_win)
            menu[name[0].lower()] = action
        else:
            if cls == Prompt:
                menu = Prompt(stdscr, title)
            else:
                menu = Menu(stdscr, False)
            if items:
                menu[title[0].lower()] = items
        curses.doupdate()
        return menu


class Prompt(Menu, object):

    def __init__(self, stdscr, msg):
        HEIGHT, WIDTH = stdscr.getmaxyx()
        self.window = curses.newwin(3,20,10,40)
        self.window.border(0)
        self.window.addstr(1,1,msg + ': ')
        self.panel = curses.panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()
        self.actions = Dict()

    def show(self):
        super(Prompt, self).show()
        curses.echo()
        instr = stdscr.getstr()
        curses.noecho()
        return instr

    def hide(self):
        super(Prompt, self).hide()
        
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


def clean_up(stdscr, ex = True):
    """
    Restore terminal to sane state.

    :param stdscr: main window
    :type stdscr: :py:obj:`curses.window`
    """
    stdscr.keypad(0)
    curses.nocbreak()
    curses.endwin()
    curses.echo()
    if ex:
        sys.exit(0)
