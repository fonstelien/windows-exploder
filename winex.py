#!/usr/bin/env python3

import urwid
from palette import palette
import resultobject
import infoline
import prompt
import presentation
import cmdhistory
import markup


class TextUserInterface(urwid.Frame):
    def __init__(self, get_markup):
        self.get_markup = get_markup
        self.resultobj = resultobject.ResultObject()

        # The 'header' widget
        self.parent_directory = infoline.ParentDirectoryWidget()
        self.prompt = prompt.PromptWidgetHandler(self.resultobj)
        self.result = infoline.ResultWidget(
            'init', resultobject.ResultObject.status_map)
        header = urwid.Pile(
            [self.parent_directory, self.prompt, urwid.Divider(), self.result])

        # The 'body' and 'footer' widgets
        self.presentation = presentation.PresentationWidget(get_markup)
        self.session = infoline.SessionInfo(cut_pos=-1, string="")

        # The cmd_history widget
        self.history_resultobj = resultobject.ResultObject()
        self.cmd_history = cmdhistory.CmdHistoryWidget(self.history_resultobj)
        self.cmd_history.add(self.resultobj)

        # Setting initial content
        self.parent_directory.update()
        self.result.update(self.resultobj.status,
                           self.resultobj.description)
        self.presentation.update(self.resultobj.presentation)

        super(TextUserInterface, self).__init__(
            header=header, body=self.presentation, footer=self.session,
            focus_part="header")

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
        if self.get_focus() == 'header':
            if key == 'enter':
                self.cmd_history.add(self.resultobj)
                self.parent_directory.update()
                self.prompt.update(None, "")
                self.result.update(self.resultobj.status,
                                   self.resultobj.description)
                self.presentation.update(self.resultobj.presentation)

            elif key == 'esc':
                self.prompt.update(None, "")

            elif key == 'down' and self.presentation.selectable():
                self.set_focus('body')

            elif key == 'up':
                self.footer = self.cmd_history
                self.set_focus('footer')

        # Focus is on cmd_history
        if self.get_focus() == 'footer':
            if key in ('up', 'down', 'enter', 'backspace') or len(key) == 1:
                self.parent_directory.update(
                    self.history_resultobj.parent_exec_wd)
                self.prompt.update(self.history_resultobj.mode_id,
                                   self.history_resultobj.base_exec_wd,
                                   self.history_resultobj.command)
                self.result.update(self.history_resultobj.status,
                                   self.history_resultobj.description)
                self.presentation.update(self.history_resultobj.presentation,
                                         force=True)

            elif key in ('esc', 'tab'):
                edit_text = ""
                if key == 'tab':
                    edit_text = self.history_resultobj.command
                self.parent_directory.update(self.resultobj.parent_exec_wd)
                self.prompt.update(edit_text=edit_text)
                self.result.update(self.resultobj.status,
                                   self.resultobj.description)
                self.presentation.update(self.resultobj.presentation)

            if key in ('esc', 'enter', 'tab'):
                self.footer = self.session
                self.set_focus('header')

        return key


if __name__ == '__main__':
    def direct_quit(key):
        if key == 'meta q':
            raise urwid.ExitMainLoop()

    color_mapper = markup.ColorMapper()
    widget = TextUserInterface(color_mapper.get_markup)
    mainloop = urwid.MainLoop(
        widget, palette=palette, unhandled_input=direct_quit, pop_ups=True)
    color_mapper.setup(mainloop)
    mainloop.run()
