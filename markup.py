import urwid
import re


class ColorMapper(object):
    """Handles the mapping of bash color codes to urwid text markup."""

    # Pattern for returning full bash color code
    # incl. escape character, etc: '[01;34m'
    fullpattern = re.compile(
        r'(\[(?:\d{1,3};)*(?:\d{1,3}m(?:\[K)?))', flags=re.UNICODE)
    # Pattern for returning only bash color codes separated by ';': '01;34'
    filtpattern = re.compile(
        r'(?:\[)((?:\d{1,3};)*(?:\d{1,3}))(?:m(?:\[K)?)', flags=re.UNICODE)

    # Mapping for str.replace of 'alternative' bash color code for 'default'
    replace_default = ('[m[K', '[0m')

    # Foreground bash to urwid color mapping
    foreground_codes = {'0': 'default',
                        '30': 'black',
                        '31': 'dark red',
                        '32': 'dark green',
                        '34': 'dark blue',
                        '35': 'dark magenta',
                        '36': 'dark cyan',
                        '37': 'light gray',
                        '90': 'dark gray',
                        '91': 'light red',
                        '92': 'light green',
                        '93': 'yellow',
                        '94': 'light blue',
                        '95': 'light magenta',
                        '96': 'light cyan',
                        '97': 'white',
                        '01': 'bold',
                        '04': 'underline',
                        '07': 'standout',
                        '05': 'blink'}

    # Background bash to urwid color mapping
    background_codes = {'40': 'black',
                        '41': 'dark red',
                        '42': 'dark green',
                        '44': 'dark blue',
                        '45': 'dark magenta',
                        '46': 'dark cyan',
                        '47': 'light gray'}

    def __init__(self):
        """Serves only for instance initialization.
        Call setup with the MainLoop instance
        after initialization."""
        self.register_palette_entry = None  # See setup()
        self.attr_names = list()

    def setup(self, mainloop):
        """Point register_palette_entry to
        MainLoop.screen.register_palette_entry()"""
        self.register_palette_entry = mainloop.screen.register_palette_entry

    def get_markup(self, string):
        """
        Searches string for bash color codes and returns urwid-type markup.
        New urwid color maps are created and new palette entries are appended
        to MainLoop's palette.

        Example:
        >>> markup('Hello [01;34mworld![0m')
        [('', Hello '), ('01;34', 'world!'), ('0', '')]
        """

        # Does string have bash color codes?
        if not self.fullpattern.search(string):
            return string

        string = string.replace(*self.replace_default)
        markup = list()
        attr_name = ''

        # Pattern.split() gives a list like
        # ['Hello ', '[01;34m', 'world!', '[0m']
        for element in self.fullpattern.split(string):
            match = self.filtpattern.fullmatch(element)

            # element is color code
            if match:
                attr_name = match.group(1)  # attr_name on the form of '01;34'

                if attr_name in self.attr_names:
                    continue
                self.attr_names.append(attr_name)

                codes = attr_name.split(';')
                attr_foreground = list()
                attr_background = list()
                for code in codes:
                    if code in self.foreground_codes:
                        attr_foreground.append(self.foreground_codes[code])
                    elif code in self.background_codes:
                        attr_background.append(self.background_codes[code])
                    # else: disregard code and use default

                # Register new attribute in MainLoop's palette
                self.register_palette_entry(attr_name,
                                            ','.join(attr_foreground),
                                            ','.join(attr_background))

            # element is text and non-empty
            elif element:
                markup.append((attr_name, element))

        return markup


class DynColorEdit(urwid.Edit):
    def __init__(self, markup, *args, **kwargs):
        self.markup = markup
        super(DynColorEdit, self).__init__(*args, **kwargs)

    def keypress(self, size, key):
        if key == 'enter':
            string = ''.join(open('colors.txt').readlines())
            markup = self.markup.markup(string)
            self.set_caption(markup)

        if key == 'esc':
            self.set_caption(self.caption)

        return super(DynColorEdit, self).keypress(size, key)


if __name__ == '__main__':
    import utils

    m = ColorMapper()
    e = DynColorEdit(m, caption="I miss you!")
    w = urwid.Filler(e, valign='top')
    loop = urwid.MainLoop(w, unhandled_input=utils.meta_q)
    m.setup(loop)
    loop.run()
