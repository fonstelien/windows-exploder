import urwid
import copy

from programstatus import ProgramStatus

class CmdHistory(object):
    def __init__(self, program_status):
        self.history = list()
        self.length = 0
        self.idx = 0
        self.search_str = ""
        self.add(program_status)
        
    def add(self, program_status):
        for item in self.history:
            if vars(program_status) == vars(item):
                self.history.remove(item)
        self.history.append(copy.copy(program_status))
        self.length = len(self.history)
        self.reset()
        
    def reset(self, search_str=""):
        self.idx = self.length - 1
        self.search_str = search_str
        
    def next(self, step, _recur_idx=0):
        if _recur_idx == self.length:
            return None
        
        self.idx = max(0, (self.idx + step) % self.length)
        item = None
        try:
            item = self.history[self.idx]
        except IndexError as e:
            raise urwid.ExitMainLoop(self.idx)

            
        if self.search_str in item.command:
            return item
        return self.next(step, _recur_idx+1)

    def last(self):
        return self.history[-1]
    
    
class CmdHistoryWidget(urwid.Edit):
    def __init__(self, program_status):
        self.program_status = program_status
        self.history = CmdHistory(program_status)
        super(CmdHistoryWidget, self).__init__(caption="Search history:")

    def add(self):
        self.history.add(self.program_status)
        
    def reset_widget(self):
        self.edit_text = ""
        self.history.reset()

    def keypress(self, size, key):
        super(CmdHistoryWidget, self).keypress(size, key)

        # Typing in search field
        if len(key) == 1 or key == 'backspace':

            # Show last item if search string is empty
            if self.edit_text == "":
                self.history.reset(search_str="")
                self.program_status.copy_state(self.history.last())
                
            # Reset history with new search_str and copy state to program_status
            elif self.edit_text not in self.program_status.command:
                self.history.reset(search_str=self.edit_text)
                state = self.history.next(-1)
                if state is None:
                    self.program_status.copy_state(self.history.last())
                else:
                    self.program_status.copy_state(self.history.next(-1))

            return key

        elif key == 'up':
            self.program_status.copy_state(self.history.next(-1))

        elif key == 'down':
            self.program_status.copy_state(self.history.next(+1))
         
        elif key == 'esc':
            self.program_status.copy_state(self.history.last())

        # elif key == 'enter':
        #     last_state = self.history.last()
        #     mode_id = last_state.mode_id
        #     self.program_status.set_result()
            
        elif key == 'tab':
            pass
            # if self.program_status.cwd != os.getcwd():
                

        if key in ('esc', 'enter', 'tab'):
            self.reset_widget()
        return key
