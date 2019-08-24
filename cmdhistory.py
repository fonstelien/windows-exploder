#!/usr/bin/env python3

import urwid
import resultobject


class _CmdHistory(object):
    def __init__(self):
        self.history = list()
        self.length = 0
        self.idx = 0
        self.search_str = ""

    def add(self, resultobj):
        for item in self.history:
            if vars(resultobj) == vars(item):
                self.history.remove(item)

        new_item = resultobject.ResultObject()
        new_item.copy_state(resultobj)
        self.history.append(new_item)
        self.length = len(self.history)
        self.idx = self.length - 1

    def set_search_str(self, search_str):
        self.idx = self.length - 1
        self.search_str = search_str

    def get_last_item(self):
        if self.length == 0:
            return None
        return self.history[-1]

    def get_curr_idx_item(self):
        return self.history[self.idx]

    def get_next_item(self, step, _recur_idx=0):
        if _recur_idx == self.length:
            return None

        self.idx = max(0, (self.idx + step) % self.length)
        item = self.history[self.idx]
        if self.search_str in item.command:
            return item
        return self.get_next_item(step, _recur_idx+1)


class CmdHistoryWidget(urwid.Edit):
    def __init__(self, resultobj):
        self.resultobj = resultobj
        self.history = _CmdHistory()
        super(CmdHistoryWidget, self).__init__(caption="Search history:")

    def add(self, resultobj):
        self.resultobj.copy_state(resultobj)
        self.history.add(resultobj)

    def reset_widget(self):
        self.set_edit_text("")
        self.history.set_search_str("")

    def keypress(self, size, key):
        super(CmdHistoryWidget, self).keypress(size, key)

        # Typing in search field
        if len(key) == 1 or key == 'backspace':
            self.history.set_search_str(self.edit_text)

            # Show last item if search string is empty
            if self.edit_text == "":
                self.resultobj.copy_state(self.history.get_last_item())

            # Set new search_str and copy state to resultobj
            elif self.edit_text not in self.resultobj.command:
                history_item = self.history.get_next_item(-1)
                if history_item is None:
                    self.resultobj.copy_state(self.history.get_last_item())
                else:
                    self.resultobj.copy_state(history_item)

            return key

        elif key == 'up':
            self.resultobj.copy_state(self.history.get_next_item(-1))

        elif key == 'down':
            self.resultobj.copy_state(self.history.get_next_item(+1))

        if key in ('esc', 'enter', 'tab'):
            self.reset_widget()
        return key
