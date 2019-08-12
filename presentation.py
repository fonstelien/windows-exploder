#!/usr/bin/env python3

import urwid
from walker import Walker


def init_widget():
    banner = urwid.BigText(markup=("programpresentation", "Windows Exploder"),
                           font=urwid.HalfBlock5x4Font())
    banner = urwid.Padding(w=banner, align="center", width="clip")
    signature = urwid.Text(
        markup=("programpresentation", "V.0.1 by Olav Fønstelien"),
        align="center")
    divider = [urwid.Divider()]*5
    return urwid.SimpleListWalker(divider+[banner, signature])


class PresentationWidget(Walker):
    def __init__(self, program_status, get_markup=None):
        self.program_status = program_status
        self.get_markup = get_markup
        super(PresentationWidget, self).__init__()
        self._selectable = False
        self.update()

    def update(self, force=False):
        presentation = self.program_status.presentation.splitlines()
        if not (presentation or force):
            return

        markup_list = list()
        for line in presentation:
            markup_list.append(self.get_markup(line))
        self.set_content(markup_list)

    def reset_widget(self):
        if self.focus is None:
            return
        self.focus_position = 0
