#!/usr/bin/env python3

import urwid

class _Editor(urwid.Edit):
    _separators = ' _-.\\/+*'
    _deleters = ('backspace', 'ctrl d', 'meta backspace', 'meta d')
    
    def __init__(self, *args, **kwargs):
        super(_Editor, self).__init__(*args, **kwargs)
        self.__caption_markup = list()
        self.__edit_text_markup = list()
        self.__edit_text = ""

    def __getattr__(self, name):
        return super(_Editor, self).__getattribute__(name)
        
    def __fast_reverse(self):
        string = self.edit_text[:self.edit_pos]
        pos = max(map(string.rfind, self._separators))
        return pos if pos > 0 else 0
    
    def __fast_forward(self):
        self.edit_pos += 1
        string = self.edit_text[self.edit_pos:]
        try:
            return self.edit_pos + min(
                filter(lambda x: x >= 0, map(string.find, self._separators)))
        except ValueError:
            return len(self.edit_text)
        
    def keypress(self, size, key):
        super(_Editor, self).keypress(size, key)

        # Walk
        if key == 'ctrl a':
            self.edit_pos = 0
        elif key == 'ctrl e':
            self.edit_pos = len(self.edit_text)
        elif key == 'ctrl b':
            self.edit_pos -= 1
        elif key == 'ctrl f':
            self.edit_pos += 1
        elif key == 'meta b':
            self.edit_pos = self.__fast_reverse()
        elif key == 'meta f':
            self.edit_pos = self.__fast_forward()

        # Deletions
        elif key == 'ctrl d':
            pos = self.edit_pos
            self.edit_text = self.edit_text[:pos] + self.edit_text[pos+1:]
        elif key == 'meta backspace':
            cut_right = self.edit_pos
            cut_left = self.__fast_reverse()
            self.edit_text = self.edit_text[:cut_left] + self.edit_text[cut_right:]
            self.edit_pos = cut_left
        elif key == 'meta d':
            cut_left = self.edit_pos
            cut_right = self.__fast_forward() + 1
            self.edit_text = self.edit_text[:cut_left] + self.edit_text[cut_right:]
            if self.edit_pos != len(self.edit_text):
                self.edit_pos -= 1
        elif key == 'ctrl k':
            self.edit_text = self.edit_text[:self.edit_pos]
        elif key == 'ctrl u':
            self.edit_text = self.edit_text[self.edit_pos:]
            self.edit_pos = 0
                    
        return key

    def start_focus(self, edit_pos):
        self.set_caption(self.__caption_markup)
        self.edit_text = self.__edit_text
        self.edit_pos = edit_pos

    def replace_marked_text(self, left_pos, right_pos, substitute=""):
        self.edit_text = \
            self.edit_text[:left_pos] + substitute + self.edit_text[right_pos:]
        self.edit_pos = left_pos + len(substitute)
        
    def end_focus(self):
        self.__caption_markup.clear()
        caption_text = self.caption
        for attrib in self.attrib:
            attr, ln = attrib
            self.__caption_markup.append((attr, caption_text[:ln]))
            caption_text = caption_text[ln:]
        self.set_caption(self.__caption_markup + [(None, self.edit_text)])

        self.__edit_text = self.edit_text
        edit_pos = self.edit_pos        
        self.edit_text = ""    
        return self.__edit_text, edit_pos
    
    def show_marking(self, edit_text_markup=list()):
        self.set_caption(self.__caption_markup + edit_text_markup)        
        
        
class _MarkerEditor(_Editor):
    def __init__(self):
        super(_MarkerEditor, self).__init__()
        self._pos0 = self._pos1 = self.edit_pos
    
    def valid_char(self, ch):
        return False

    def keypress(self, size, key):
        # Override deletion commands
        if key in self._deleters:
            return key
        
        super(_MarkerEditor, self).keypress(size, key)
        self._pos1 = self.edit_pos
        return key

    def start_focus(self, edit_text, edit_pos):
        self.edit_text = edit_text
        self.edit_pos = edit_pos
        self._pos0 = self._pos1 = edit_pos

    def end_focus(self):
        edit_pos = self.edit_pos
        self.edit_text = ""
        return edit_pos

    def get_left_right_pos(self):
        if self._pos0 < self._pos1:
            return (self._pos0, self._pos1)
        return (self._pos1, self._pos0)
    
    def get_markup(self):
        edit_text_markup = list()
        l,r = self.get_left_right_pos()
        p = self.edit_pos

        marker_right_pos = True if p == r else False
        marker = self.edit_text[p] if p != len(self.edit_text) else " "
        left_plain = self.edit_text[:l]

        if marker_right_pos:
            marked = self.edit_text[l:r]        
            right_plain = self.edit_text[r+1:]
        else:
            marked = self.edit_text[l+1:r]
            right_plain = self.edit_text[r:]
        
        if left_plain:
            edit_text_markup.append((None, left_plain))
        if not marker_right_pos:
            edit_text_markup.append(('marker_left', marker))
        if marked:
            edit_text_markup.append(('marked', marked))
        if marker_right_pos:
            edit_text_markup.append(('marker_right', marker))
        if right_plain:
            edit_text_markup.append((None, right_plain))
                    
        return edit_text_markup
    
        
class Editor(urwid.Columns):
    def __init__(self, *args, **kwargs):
        self._editor = _Editor(*args, **kwargs)
        self._marker_editor = _MarkerEditor()
        self._marker_mode = False
        super(Editor, self).__init__([self._editor, (0, self._marker_editor)])

    def __getattr__(self, name):
        if name in _Editor.__dict__.keys() or name in urwid.Edit.__dict__.keys():
            return self._editor.__getattr__(name)
        return super(Editor, self).__getattr__(name)
        
    def __setattr__(self, name, value):
        if name in _Editor.__dict__.keys() or name in urwid.Edit.__dict__.keys():
            self._editor.__setattr__(name, value)
        else:
            super(Editor, self).__setattr__(name, value)
            
    def set_caption(self, markup=list()):
        self._editor.set_caption(markup)

    def set_edit_text(self, edit_text=""):
        self._editor.set_edit_text(edit_text)

    def set_edit_pos(self, edit_pos=0):
        self._editor.edit_pos = edit_pos
    
    def keypress(self, size, key):
        super(Editor, self).keypress(size, key)

        # Override urwid built-in move focus when press right at end of _editor.edit_text
        if self.focus is self._marker_editor and not self._marker_mode:
            self.set_focus(self._editor)
        elif self.focus is self._editor and self._marker_mode:
            self.set_focus(self._marker_editor)

        # Editor is in _editor mode
        if not self._marker_mode:
            # Enter _marker_editor mode
            if key == '<0>':
                self.set_focus(self._marker_editor)
                self._marker_mode = True
                edit_text, edit_pos = self._editor.end_focus()
                self._marker_editor.start_focus(edit_text, edit_pos)
                markup = self._marker_editor.get_markup()
                self._editor.show_marking(markup)
                
        # Editor is in _marker_editor mode
        else:
            # Escape from _marker_mode
            if key in ('esc', '<0>', 'enter'):
                self.set_focus(self._editor)
                self._marker_mode = False
                edit_pos = self._marker_editor.end_focus()
                self._editor.start_focus(edit_pos)

            elif key == 'backspace':
                self.set_focus(self._editor)
                self._marker_mode = False
                l,r = self._marker_editor.get_left_right_pos()
                edit_pos = self._marker_editor.end_focus()
                self._editor.start_focus(edit_pos)
                self._editor.replace_marked_text(l, r, substitute="")
                
            # Update _editor view
            else:
                markup = self._marker_editor.get_markup()
                self._editor.show_marking(markup)
                
        return key


if __name__ == '__main__':
    palette = [('marked', 'black', 'light green'),
               ('marker_left', 'black, bold, underline, blink', 'light green'),
               ('marker_right', 'standout, bold, underline, blink', ''),
               ('attr1', 'dark green', ''),
               ('attr2', 'dark red', '')]

    def meta_q(key):
        if key == "meta q":
            raise urwid.ExitMainLoop()

    e = Editor(caption=[('attr1', "directory/"), ('attr2', " (mode) ")], edit_text="Hello my darling! I miss you!")
    urwid.MainLoop(urwid.Filler(e, valign='top'), palette=palette, unhandled_input=meta_q).run()
