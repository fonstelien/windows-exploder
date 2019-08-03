#!/usr/bin/env python3

import urwid

def init_widget():
    banner = urwid.BigText(markup=("programpresentation", "Windows Exploder"),
                           font=urwid.HalfBlock5x4Font())
    banner = urwid.Padding(w=banner, align="center", width="clip")
    signature = urwid.Text(markup=("programpresentation", "V.0.1 by Olav Fønstelien"),
                           align="center")
    divider = [urwid.Divider()]*5
    return divider+[banner, signature]


class PresentationWidget(urwid.ListBox):
    def __init__(self, program_status):
        self.program_status = program_status
        super(PresentationWidget, self).__init__(urwid.SimpleListWalker(init_widget()))
        
    def update(self, force=False):
        lines = list()
        presentation = self.program_status.presentation.splitlines()
        if not (presentation or force):
            return
        for line in presentation:
            lines.append(urwid.Edit(line))
        self.body = lines

    def set_focus_highlight(self, highlight=True):
        if self.focus is None or not self.focus.selectable():
            return
        markup = self.focus.caption
        if highlight:
            markup = ('infoline', markup)
        self.focus.set_caption([markup])

    def reset_widget(self):
        self.set_focus_highlight(False)
        
    def keypress(self, size, key):
        if not self.focus.selectable():
            return super(PresentationWidget, self).keypress(size, key)
        
        if key in ('up', 'down', 'page up', 'page down', 'home', 'end'):
            self.set_focus_highlight(False)
            if key == 'up':
                self.focus_position = max(self.focus_position-1, 0)
            elif key == 'down':
                self.focus_position = min(self.focus_position+1, len(self.body)-1)
            else:
                super(PresentationWidget, self).keypress(size, key)
            self.set_focus_highlight(True)
        return key

        
if __name__ == "__main__":
    import utils
    from palette import palette
    from programstatus import ProgramStatus
    w = PresentationWidget(ProgramStatus('parent/directory', 'def'))
    urwid.MainLoop(w, palette=palette, unhandled_input=utils.meta_q).run()

