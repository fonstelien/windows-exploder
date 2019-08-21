#!/usr/bin/env python3

palette = [('directory', 'dark blue, bold', ''),
           ('mode', 'dark green, bold', ''),
           ('marked', 'black', 'light green'),
           ('marker_left', 'black, bold, underline, blink', 'light green'),
           ('marker_right', 'standout, bold, underline, blink', ''),
           ('infoline', 'standout', ''),
           ('init', 'dark blue, bold', 'light gray'),
           ('programpresentation', 'dark blue, bold', ''),
           ('success', 'black', 'dark green'),
           ('failure', 'black', 'dark red'),
           ('error', 'black', 'dark red'),
           ('prompt', 'black', 'yellow'),
           ('dropdown_editor', '', 'dark gray'),
           ('dropdown_plain', 'white', 'dark green'),
           ('dropdown_marked', 'dark red, bold', 'dark green'),
           ('dropdown_walk', 'black', 'light green')]


if __name__ == '__main__':
    """Displays each of the palette color schemes.
    'meta q' ends the program."""
    import urwid
    import utils

    colors = list()
    for p in palette:
        markup = (p[0], "TEST STRING test string "*3)
        colors.append(urwid.Divider())
        colors.append(urwid.Text(markup))
    utils.showwidget(urwid.Pile(colors), palette=palette)
