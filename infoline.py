#!/usr/bin/env python3

import urwid

class InfoLine(urwid.AttrMap):
    def __init__(self, program_status, cut_position=10, separator_string="...", attr_map="infoline", **kwargs):
        super(InfoLine, self).__init__(w=urwid.Text(markup=""), attr_map=attr_map)
        self.program_status = program_status
        self.cut_position = cut_position
        self.separator_string = separator_string
        self.separator_string_length = len(separator_string)
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
            if self.separator_string_length >= maxcol:
                show_string = self.separator_string[:maxcol]
            elif self.cut_position == -1 or (self.cut_position + self.separator_string_length >= maxcol):
                show_string = show_string[:maxcol-self.separator_string_length] + self.separator_string
            else:
                cut_right = self.cut_position + self.separator_string_length + self.full_text_length - maxcol
                show_string = show_string[:self.cut_position] + self.separator_string + show_string[cut_right:]
        self.original_widget.set_text(show_string)
        return super(InfoLine, self).render(size)


class ParentDirectoryWidget(InfoLine):        
    def update(self):
        self.full_text = self.program_status.parent + "/"
        self.full_text_length = len(self.full_text)
        self._invalidate()


class SessionInfo(InfoLine):
    def update(self, string):
        self.full_text = f"Session started at ##:##:##"
        self.full_text_length = len(self.full_text)
        self._invalidate()
        
        
class ResultStatusWidget(InfoLine):
    def update(self, show_string=""):
        self.full_text = "   " + show_string + "   "
        self.full_text_length = len(self.full_text)

        
class ResultStatusWidgetWrapper(urwid.WidgetWrap):
    def __init__(self, program_status):
        self.program_status = program_status
        self.status = dict()
        for status, string in program_status.status_map.items():
            self.status[status] = ResultStatusWidget(
                program_status=None, cut_position=-1, attr_map=status, show_string=string)
        super(ResultStatusWidgetWrapper, self).__init__(
            self.status[self.program_status.status])

    def update(self):
        self._w = self.status[self.program_status.status]

        
class ResultDescriptionWidget(urwid.AttrMap):
    def __init__(self, program_status):
        self.program_status = program_status
        self.default_attr_map = {None: "infoline"}
        super(ResultDescriptionWidget, self).__init__(
            w=urwid.Text(markup=""), attr_map=self.default_attr_map)
        self.update()
        
    def update(self):
        self.original_widget.set_text(self.program_status.description)
        if self.program_status.description == "":
            self.set_attr_map({None: ""})
        else:
            self.set_attr_map(self.default_attr_map)

            
class ResultWidget(urwid.Columns):
    def __init__(self, program_status):
        self.program_status = program_status
        self.status = ResultStatusWidgetWrapper(program_status)
        self.description = ResultDescriptionWidget(program_status)
        super(ResultWidget, self).__init__([("pack", self.status), self.description])

    def update(self):
        self.status.update()
        self.description.update()
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
