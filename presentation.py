#!/usr/bin/env python3

import urwid
import walker


def init_widget():
    banner = urwid.BigText(markup=("programpresentation", "Windows Exploder"),
                           font=urwid.HalfBlock5x4Font())
    banner = urwid.Padding(w=banner, align="center", width="clip")
    signature = urwid.Text(
        markup=("programpresentation", "V.0.1 by Olav Fønstelien"),
        align="center")
    divider = [urwid.Divider()]*5
    return urwid.SimpleListWalker(divider+[banner, signature])


class PresentationWidget(walker.Walker):
    def __init__(self, get_markup):
        self.get_markup = get_markup  # A function object
        super(PresentationWidget, self).__init__()
        self._selectable = False
        self.update()

    def update(self, presentation="", force=False):
        if not (presentation or force):
            return

        presentation = presentation.splitlines()
        markup_list = list()
        for line in presentation:
            markup_list.append(self.get_markup(line))
        self.set_content(markup_list)

    def reset_widget(self):
        if self.focus is None:
            return
        self.focus_position = 0
