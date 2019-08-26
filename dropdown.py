#!/usr/bin/env python3

import urwid
import editor
import walker


class DropDown(urwid.Frame):
    """A pop up widget for auto completing user input. The auto complete options
    are set with the set_content() method, content is filtered with the
    search() method, and selections are made with 'enter' or 'tab'."""

    signals = ['close', 'render']

    def __init__(self):
        self.editor = editor.Editor()
        self.walker = walker.Walker(focus_attr='dropdown_walk')
        super(DropDown, self).__init__(
            header=urwid.AttrMap(self.editor, attr_map='dropdown_editor'),
            body=urwid.AttrMap(self.walker, attr_map='dropdown_plain'),
            focus_part='header')
        # The longest string in the options range. Updated in set_content()
        self.max_width = 1
        self.selection = ''  # The selected option returned to handling widget
        self._selectable = False

    def set_content(self, content_list):
        """Sets the pop up content_list. The max_width property is also
        set, and selectable() returns True if content_list is non-empty."""
        self.walker.set_content(content_list)
        self._selectable = self.walker.selectable()
        if self._selectable:
            # +1 for the cursor
            self.max_width = max(map(len, content_list)) + 1
        else:
            self.max_width = 1

    def search(self, edit_text):
        """Set edit_text in the pop up editor. Calls Walker.filter_content()
        with edit_text as argument."""
        self.editor.edit_text = edit_text
        self.editor.edit_pos = len(edit_text)
        self.walker.filter_content(edit_text,
                                   attr_marked='dropdown_marked',
                                   attr_plain='dropdown_plain')

    def has_match(self, search_str):
        """Does 'search_str' have a match in the current options list? The empty
        string returns False"""
        if search_str == '':
            return False
        return self.walker.has_match(search_str)

    @property
    def curr_height(self):
        """Total number of rows in the pop up,"""
        return self.walker.length() + 1  # Add 1 row for the edit line

    def keypress(self, size, key):
        """Implementation of the keypress() method. The pop up will not return
        key to overlaying widget"""
        # This lets the user still modify the edit_text when focus is on 'body'
        if len(key) == 1 or key in self.editor._deleters:
            self.set_focus('header')
            super(DropDown, self).keypress(size, key)
            self.walker.filter_content(self.editor.edit_text,
                                       attr_marked='dropdown_marked',
                                       attr_plain='dropdown_plain')

            # Signal 'close' and return edit_text to calling widget
            if not self.has_match(self.editor.edit_text):
                self.selection = self.editor.edit_text
                self._emit('close')
                return key

            self._emit('render')
            return None  # Do not return the key

        # Actions to complete after sending key to underlaying widget
        super(DropDown, self).keypress(size, key)

        if key == 'down' and self.get_focus() == 'header':
            self.set_focus('body')

        # Signal 'close' and return selection to calling widget
        elif key in ('enter', 'tab'):
            self.set_focus('body')  # Return first if no selection
            self.selection = self.editor.edit_text
            if self.walker.length() > 0:  # Selection possible?
                self.selection = self.walker.get_selected_message()
            self.set_focus('header')
            self._emit('close')

        elif key == 'esc':
            self.selection = self.editor.edit_text
            self._emit('close')

        return None  # Do not return the key
