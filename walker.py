#!/usr/bin/env python3

import re
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
    def __init__(self, w, focus_attr):
        super(_Line, self).__init__(w, attr_map=None, focus_map=focus_attr)

    def render(self, size, focus=False):
        if focus:
            self.original_widget.show_plain()
        else:
            self.original_widget.show_markup()
        return super(_Line, self).render(size, focus)

    def __getattr__(self, name):
        return object.__getattribute__(self.original_widget, name)


class _Lines(urwid.SimpleListWalker):
    def __init__(self, focus_attr):
        self.focus_attr = focus_attr
        self.checkbox = False
        super(_Lines, self).__init__(list())

    def set_content(self, markup_list, checkbox=False):
        self.contents.clear()
        self.checkbox = checkbox

        for markup in markup_list:
            w = _CheckBox(markup) if checkbox else _Text(markup)
            self.contents.append(_Line(w, self.focus_attr))

    def get_selected_message(self):
        # Contains _Text objects. Return only text
        if not self.checkbox:
            return self.get_focus().get_string()

        # Contains _CheckBox objects. Return text of all checked boxes
        message = list()
        for cb in self:
            message.append(cb.get_string())
        return message


class Walker(urwid.ListBox):
    def __init__(self, markup_list=list(), checkbox=False,
                 focus_attr='infoline'):
        super(Walker, self).__init__(body=_Lines(focus_attr))
        self.original_body = self.body  # Used when calling filter_content()
        self.set_content(markup_list, checkbox)

    def set_content(self, markup_list, checkbox=False):
        self.body = self.original_body
        self.body.set_content(markup_list, checkbox)
        self._selectable = True if len(self.body) > 0 else False

    def filter_content(self, search_pattern, attr_marked='', attr_plain=''):
        if search_pattern == '':
            self.body = self.original_body
            return

        # Replace body with a new _Lines object containing the filtered list
        filtered_list = list()
        try:
            pattern = re.compile(rf'(.*?)({search_pattern})(.*)',
                                 flags=re.IGNORECASE | re.UNICODE)
            for line in self.original_body:
                match = pattern.match(line.get_string())
                if match:
                    if not attr_marked:
                        filtered_list.append(match.group(0))
                        continue

                    left_str, match_str, right_str = match.groups()
                    markup = [(attr_plain, left_str)]
                    markup += [(attr_marked, match_str)]
                    markup += [(attr_plain, right_str)]
                    filtered_list.append(markup)

            self.body = _Lines(self.body.focus_attr)
            self.body.set_content(filtered_list, self.original_body.checkbox)
            return

        except re.error:
            pass
        except ValueError:
            pass
        self.body = self.original_body

    def has_match(self, search_str):
        try:
            pattern = re.compile(rf'(.*?)({search_str})(.*)',
                                 flags=re.IGNORECASE | re.UNICODE)
            for line in self.original_body:
                if pattern.search(line.get_string()):
                    return True
        except re.error:
            pass

        return False

    def set_focus_attr(self, attr):
        self.body.focus_attr = attr

    def get_focus_attr(self):
        return self.body.focus_attr

    def get_selected_message(self):
        return self.focus.get_string()

    def length(self):
        return len(self.body)

    def keypress(self, size, key):
        if key == 'up':
            self.focus_position = max(self.focus_position-1, 0)
        elif key == 'down':
            self.focus_position = min(self.focus_position+1, len(self.body)-1)
        else:
            super(Walker, self).keypress(size, key)

        self._invalidate()
        return key


if __name__ == '__main__':
    import utils
    from markup import ColorMapper

    color_mapper = ColorMapper()
    walker = Walker()
    loop = urwid.MainLoop(walker, unhandled_input=utils.meta_q,
                          palette=[('infoline', 'standout', '')])
    color_mapper.setup(loop)

    markup_list = list()
    for line in open('colors.txt').read().splitlines():
        markup_list.append(color_mapper.get_markup(line))

    walker.update(markup_list)
    loop.run()
