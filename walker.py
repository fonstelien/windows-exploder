#!/usr/bin/env python3

import urwid

class _CheckBox(urwid.CheckBox):
    def __init__(self, markup, *args, **kwargs):
        self.markup = markup
        super(_CheckBox, self).__init__(label=markup, *args, **kwargs)
    
    def get_string(self):
        return self.get_label()

    def show_markup(self):
        self.set_label(self.markup)

    def show_plain(self):
        self.set_label(self.get_label())

        
class _Text(urwid.Text):
    def __init__(self, markup, *args, **kwargs):
        self.markup = markup
        super(_Text, self).__init__(markup=markup, *args, **kwargs)

    def get_string(self):
        return self.text

    def show_markup(self):
        self.set_text(self.markup)

    def show_plain(self):
        self.set_text(self.text)    

        
class _Line(urwid.AttrMap):
    def __init__(self, w):
        super(_Line, self).__init__(w, attr_map=None, focus_map='infoline')

    def render(self, size, focus=False):
        if focus:
            self.original_widget.show_plain()
        else:
            self.original_widget.show_markup()
        return super(_Line, self).render(size, focus)
        
    def __getattr__(self, name):
        return object.__getattribute__(self.original_widget, name)

            
class _Lines(urwid.SimpleListWalker):
    def __init__(self, markup_list=list(), checkbox=False):
        self.checkbox = checkbox
        super(_Lines, self).__init__(list())
        self.update(markup_list, checkbox)  # populate the _Lines.contents object
        
    def update(self, markup_list=list(), checkbox=False):
        self.contents.clear()
        if self.checkbox != checkbox:
            self.checkbox = checkbox
        if not markup_list:
            return

        wtype = _CheckBox if checkbox else _Text
        for markup in markup_list:
            self.contents.append(_Line(wtype(markup)))

        
class Walker(urwid.ListBox):
    def __init__(self, markup_list=list()):
        self.msg_buffer = ""
        super(Walker, self).__init__(body=_Lines(markup_list))

    def update(self, markup_list):
        self.body.update(markup_list)
        
    def keypress(self, size, key):
        if key == 'up':
            self.focus_position = max(self.focus_position-1, 0)
        elif key == 'down':
            self.focus_position = min(self.focus_position+1, len(self.body)-1)
        elif key == 'enter':
            self.msg_buffer = self.focus.get_string()
        else:
            super(Walker, self).keypress(size, key)

        return key


if __name__ == '__main__':
    import utils
    from markup import ColorMapper
    
    color_mapper = ColorMapper()
    walker = Walker()
    loop = urwid.MainLoop(walker, unhandled_input=utils.meta_q, palette=[('infoline', 'standout', '')])
    color_mapper.setup(loop)

    markup_list = list()
    for line in open('colors.txt').read().splitlines():
        markup_list.append(color_mapper.markup(line))

    walker.update(markup_list)
    loop.run()
