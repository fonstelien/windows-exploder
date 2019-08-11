#!/usr/bin/env python3

import subprocess
import urwid
import editor
import walker


class DropDown(urwid.Frame):
    signals = ['close']

    def __init__(self):
        self.editor = editor.Editor()
        self.msg_buffer = list()  # list object for message from Walker object
        self.walker = walker.Walker(msg_buffer=self.msg_buffer)
        super(DropDown, self).__init__(header=self.editor, body=self.walker,
                                       focus_part='header')
        self.full_range_list = list()  # The full range of autocomplete options
        self.full_range_string = ""    # range as '\n'.join(full_range_list)

    def _set_walker_contents(self):
        if self.editor.edit_text == "":
            return self.walker.show(self.full_range_list)
        subproc = subprocess.run(
            f"echo \"{self.full_range_string}\" | \
            grep {self.editor.edit_text}",
            shell=True, capture_output=True, encoding='UTF-8')
        self.walker.show(subproc.stdout.splitlines())

    def init_new_word(self, search_str, full_range_list):
        self.editor.edit_text = search_str
        self.editor.edit_pos = len(search_str)
        self.full_range_list = full_range_list
        self.full_range_string = '\n'.join(full_range_list)
        self._set_walker_contents()

    def keypress(self, size, key):
        super(DropDown, self).keypress(size, key)

        if key == 'down' and self.focus is self.editor:
            self.set_focus('body')

        elif key in ('enter', 'tab') and self.focus is self.walker:
            self.walker.set_message()
            self.editor.edit_text = self.msg_buffer[0]
            self.editor.edit_pos = len(self.editor.edit_text)
            self.msg_buffer.clear()
            self.set_focus('header')
            self._emit('close')

        elif len(key) == 1 or key in self.editor._deleters:
            self._set_walker_contents()

        return key
