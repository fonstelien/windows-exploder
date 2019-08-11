import urwid

def meta_q(key):
    if key == "meta q":
        raise urwid.ExitMainLoop()

def showwidget(w, palette=None, filler=True):
    w = urwid.Filler(w, valign="top") if filler else w
    urwid.MainLoop(w, unhandled_input=meta_q, palette=palette).run()    
    
class Showkeys(urwid.Edit):
    def keypress(self, size, key):
        self.edit_text += f"<{key}> "
        self.set_edit_pos(len(self.edit_text))
        return key

def showkeys():
    showwidget(Showkeys())

def showbig(text, font=urwid.HalfBlock5x4Font()):
    bt = urwid.ShowBig(text, font)
    pd = urwid.Padding(bt, width="clip")
    show_widget(pd)
