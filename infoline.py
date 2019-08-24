#!/usr/bin/env python3

import urwid


class InfoLine(urwid.AttrMap):
    def __init__(self, cut_pos=10, separator_str="...",
                 attr_map="infoline", **kwargs):
        super(InfoLine, self).__init__(
            w=urwid.Text(markup=""), attr_map=attr_map)
        self.cut_pos = cut_pos
        self.separator_str = separator_str
        self.separator_str_len = len(separator_str)
        self.full_text = ""
        self.full_text_length = 0
        self.update(**kwargs)
        self.render((1000,))

    def update(self, **kwargs):
        '''Abstract method which sets the InfoLine text.
        Should set the full_text and full_text_length properties.'''
        pass

    def rows(self, size, focus=False):
        return 1

    def render(self, size, focus=False):
        (maxcol, ) = size
        show_string = self.full_text
        if self.full_text_length > maxcol:
            if self.separator_str_len >= maxcol:
                show_string = self.separator_str[:maxcol]
            elif self.cut_pos == -1 or (self.cut_pos +
                                        self.separator_str_len >= maxcol):
                show_string = (show_string[:maxcol-self.separator_str_len] +
                               self.separator_str)
            else:
                cut_right = (self.cut_pos + self.separator_str_len +
                             self.full_text_length - maxcol)
                show_string = (show_string[:self.cut_pos] +
                               self.separator_str + show_string[cut_right:])
        self.original_widget.set_text(show_string)
        return super(InfoLine, self).render(size)


class ParentDirectoryWidget(InfoLine):
    def update(self, parent_directory=""):
        self.full_text = parent_directory + "/"
        self.full_text_length = len(self.full_text)
        self._invalidate()


class SessionInfo(InfoLine):
    def update(self, string=""):
        self.full_text = f"Session started at ##:##:##"
        self.full_text_length = len(self.full_text)
        self._invalidate()


class ResultStatusWidget(InfoLine):
    def update(self, show_string=""):
        blanks = ' '*3
        self.full_text = blanks + show_string + blanks
        self.full_text_length = len(self.full_text)


class ResultStatusWidgetWrapper(urwid.WidgetWrap):
    def __init__(self, init_status, status_map):
        self.status = dict()
        for status, string in status_map.items():
            self.status[status] = ResultStatusWidget(
                cut_pos=-1, attr_map=status, show_string=string)
        super(ResultStatusWidgetWrapper, self).__init__(
            self.status[init_status])

    def update(self, status):
        self._w = self.status[status]


class ResultDescriptionWidget(urwid.AttrMap):
    def __init__(self):
        self.default_attr_map = {None: "infoline"}
        super(ResultDescriptionWidget, self).__init__(
            w=urwid.Text(markup=""), attr_map=self.default_attr_map)
        self.update()

    def update(self, description=""):
        self.original_widget.set_text(description)
        if description == "":
            self.set_attr_map({None: ""})
        else:
            self.set_attr_map(self.default_attr_map)


class ResultWidget(urwid.Columns):
    def __init__(self, init_status, result_map):
        self.status = ResultStatusWidgetWrapper(init_status, result_map)
        self.description = ResultDescriptionWidget()
        super(ResultWidget, self).__init__(
            [("pack", self.status), self.description])

    def update(self, status, description):
        self.status.update(status)
        self.description.update(description)
        self._invalidate()


if __name__ == "__main__":
    from programstatus import ProgramStatus
    from palette import palette

    program_status = ProgramStatus("parent/directory/is/far/far/down/in/the/file/structure/working-dir", "cmd")
    program_status.description = "That really did not go very well. Try something different next time!"
    parent = ParentDirectoryWidget(program_status)
    result = ResultWidget(program_status)
    widget = urwid.Pile([parent, result])

    urwid.MainLoop(urwid.Filler(widget, valign="top"), palette=palette).run()
