#!/usr/bin/env python3

import urwid
import editor
import walker


class DropDown(urwid.Frame):
    signals = ['close', 'render']

    def __init__(self):
        self.editor = editor.Editor()
        self.walker = walker.Walker(focus_attr='dropdown_walk')
        super(DropDown, self).__init__(
            header=self.editor, focus_part='header',
            body=urwid.AttrMap(self.walker, attr_map='dropdown_plain'))
        # The longest string in the options range. Updated in init_new_word()
        self.max_width = 0
        self.selection = ''  # The selected option returned to handling widget

    def init_new_word(self, search_str, full_range_list):
        self.editor.edit_text = search_str
        self.editor.edit_pos = len(search_str)
        self.walker.set_content(full_range_list)
        self.max_width = max(map(len, full_range_list))
        self.walker.filter_content(self.editor.edit_text,
                                   attr_marked='dropdown_marked',
                                   attr_plain='dropdown_plain')

    @property
    def curr_height(self):
        """Total number of rows in the pop up, incl. 1 row for the editor."""
        return self.walker.length() + 1

    def keypress(self, size, key):
        # This lets the user still modify the edit_text when focus is on 'body'
        if len(key) == 1 or key in self.editor._deleters:
            self.set_focus('header')
            super(DropDown, self).keypress(size, key)
            self.walker.filter_content(self.editor.edit_text,
                                       attr_marked='dropdown_marked',
                                       attr_plain='dropdown_plain')
            self._emit('render')
            return key

        # Actions to complete after sending key to underlaying widget
        super(DropDown, self).keypress(size, key)

        if key == 'down' and self.get_focus() == 'header':
            self.set_focus('body')

        elif key in ('enter', 'tab') and self.get_focus() == 'body':
            self.editor.edit_text = self.walker.get_selected_message()
            self.editor.edit_pos = len(self.editor.edit_text)
            self.selection = self.walker.get_selected_message()
            self.set_focus('header')
            self._emit('close')

        return key
