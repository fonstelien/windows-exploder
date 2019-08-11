#!/usr/bin/env python3

import urwid
import os

from palette import palette
from programstatus import ProgramStatus
from infoline import ParentDirectoryWidget, SessionInfo, ResultWidget
from prompt import DefaultMode, PromptWidgetHandler
from presentation import PresentationWidget
from cmdhistory import CmdHistoryWidget
from markup import ColorMapper

class TextUserInterface(urwid.Frame):
    def __init__(self, program_status, get_markup):
        self.program_status = program_status
        self.get_markup = get_markup
        self.cmd_history = CmdHistoryWidget(program_status)

        self.parent_directory = ParentDirectoryWidget(program_status)
        self.prompt = PromptWidgetHandler(program_status)
        self.result = ResultWidget(program_status)
        header = urwid.Pile([
            self.parent_directory,
            self.prompt,
            urwid.Divider(),
            self.result])

        self.presentation = PresentationWidget(program_status, get_markup)
        self.session = SessionInfo(program_status=None, cut_position=-1, string="")
        super(TextUserInterface, self).__init__(body=self.presentation,
            header=header, footer=self.session, focus_part="header")

    def keypress(self, size, key):
        super(TextUserInterface, self).keypress(size, key)

        # Focus prompt widget
        if key == 'meta e':
            self.set_focus('header')
            self.prompt.reset_widget()
            self.presentation.reset_widget()
            if self.footer is self.cmd_history:
                self.cmd_history.reset_widget()
                self.footer = self.session

        # Focus presentation widget
        elif key == 'meta w' and self.presentation.selectable():
            self.set_focus('body')

        # Focus command history widget
        elif key == 'meta s':
            self.footer = self.cmd_history
            self.set_focus('footer')
            self.presentation.reset_widget()

        # Focus is on prompt
        if self.focus is self.header:        
            if key == 'enter':
                self.cmd_history.add()
                self.parent_directory.update()
                self.prompt.update()
                self.result.update()
                self.presentation.update()

            elif key == 'esc':
                self.prompt.update()
                self.result.update()

            elif key in ('up', 'down'):
                self.footer = self.cmd_history
                self.set_focus('footer')

        # Focus is on cmd_history
        if self.focus is self.footer:
            if key in ('up', 'down', 'esc', 'enter', 'tab', 'backspace') or len(key) == 1:
                self.parent_directory.update()
                self.prompt.update(reset=False)
                self.result.update()
                self.presentation.update(force=True)

            if key == 'esc':
                self.prompt.update(reset=True)

            if key in ('esc', 'enter', 'tab'):
                self.footer = self.session
                self.set_focus('header')

        return key


if __name__ == '__main__':
    def direct_quit(key):
        if key == 'meta q':
            raise urwid.ExitMainLoop()

    program_status = ProgramStatus()
    color_mapper = ColorMapper()
    widget = TextUserInterface(program_status, color_mapper.get_markup)
    mainloop = urwid.MainLoop(widget, palette=palette, unhandled_input=direct_quit)
    color_mapper.setup(mainloop)
    mainloop.run()
