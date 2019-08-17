#!/usr/bin/env python3

import urwid
import os
import subprocess

import editor
import dropdown


class PromptEditor(editor.Editor):
    signals = ['open']
    mode_id = '---'

    def __init__(self, program_status):
        self.program_status = program_status
        self.change_mode = ''
        super(PromptEditor, self).__init__(caption=self._get_caption(),
                                           edit_text=program_status.command)

    def _get_caption(self):
        directory_map = ('directory', self.program_status.directory + "/")
        mode_map = ('mode', f" ({self.mode_id}) ")
        return [directory_map, mode_map]

    def update(self):
        self.set_caption(self._get_caption())
        self.set_edit_text(self.program_status.command)
        self.set_edit_pos(len(self.edit_text))

    def reset_widget(self):
        self.set_edit_text("")
        self.change_mode = ''

    def keypress(self, size, key):
        super(PromptEditor, self).keypress(size, key)

        if key == 'enter':
            self._evaluate()

        # Handling auto_complete on calling widget
        elif (len(key) == 1 or key in self._deleters) and \
             (self.edit_pos - self.start_of_word_pos()) > 1:
            self._emit('open', {'force': False})
        elif key == 'tab':
            self._emit('open', {'force': True})
        elif key == 'meta q':
            raise urwid.ExitMainLoop()

    def _evaluate(self):
        def cwd_content():
            subproc = subprocess.run(
                "ls -lp | grep -v /$ ; tree -L 2 -dD",
                shell=True, capture_output=True, encoding='UTF-8')
            return subproc.stdout

        args = self.edit_text.split()

        # List cwd contents
        if not args:
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'success',
                presentation=cwd_content())
            return

        # Change mode
        if args[0] == 'mode':
            if len(args) > 1:
                # Rest is handled by PromptWidgetHandler
                self.change_mode = args[1]
            else:
                self.program_status.set_result(
                    self.mode_id, self.edit_text, 'failure',
                    description="mode: missing argument")
            return

        # Change directory
        if args[0] == 'cd':
            if len(args) > 1:
                new_directory = ' '.join(args[1:])
            else:
                new_directory = os.path.expanduser('~')
            try:
                os.chdir(new_directory)
                self.program_status.set_result(
                    self.mode_id, self.edit_text, 'success',
                    presentation=cwd_content())
            except FileNotFoundError:
                self.program_status.set_result(
                    self.mode_id, self.edit_text, 'failure',
                    description=f"No such file or directory: \
                    '{new_directory}'")
            except NotADirectoryError:
                self.program_status.set_result(
                    self.mode_id, self.edit_text, 'failure',
                    description=f"Not a directory: '{new_directory}'")
            return

        # Run bash command
        try:
            subproc = subprocess.run(
                self.edit_text, shell=True, capture_output=True,
                encoding='UTF-8')
            if subproc.returncode == 0:
                self.program_status.set_result(
                    self.mode_id, self.edit_text, 'success',
                    presentation=subproc.stdout)
            else:
                self.program_status.set_result(
                    self.mode_id, self.edit_text, 'failure',
                    description=subproc.stderr)
        except Exception as e:
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'error',
                description=f"Exception raised: {e}")


class DefaultMode(PromptEditor):
    mode_id = 'def'


class AltMode(PromptEditor):
    mode_id = 'alt'


class PromptWidgetHandler(urwid.PopUpLauncher):
    modes = {DefaultMode.mode_id: DefaultMode,
             AltMode.mode_id: AltMode}

    def __init__(self, program_status):
        self.program_status = program_status
        self.editors = dict()
        super(PromptWidgetHandler, self).__init__(
            self._init_mode(program_status.mode_id))

        self.auto_complete = dropdown.DropDown()
        urwid.connect_signal(
            self.auto_complete, 'close', lambda x: self.close_pop_up())
        urwid.connect_signal(
            self.auto_complete, 'render', lambda x: self._invalidate())

        # Editor.edit_text's parts to left and right part of the search_str
        # in open_pop_up()
        self.left_string = ""
        self.right_string = ""

        # pop_up dimensionging and placement
        self.pop_up_parameters = {
            'left': 0, 'top': 0, 'overlay_height': 0, 'overlay_width': 0}
        self.max_overlay_height = 8
        self.max_size = None  # (maxcol,) -- the size parameter to render()

    def _init_mode(self, mode_id):
        editor = self.modes[mode_id](self.program_status)
        urwid.connect_signal(editor, 'open',
                             lambda x, kwarg: self.open_pop_up(**kwarg))
        self.editors[mode_id] = editor
        return editor

    def update(self, reset=True):
        self.original_widget.update()
        if reset:
            self.reset_widget()

    def reset_widget(self):
        self.original_widget.reset_widget()

    def keypress(self, size, key):
        super(PromptWidgetHandler, self).keypress(size, key)
        if key == 'enter':

            # Change mode
            if self.original_widget.change_mode:
                curr_mode_id = self.original_widget.mode_id
                next_mode_id = self.original_widget.change_mode
                command = self.original_widget.edit_text

                # Load prev. used mode
                if next_mode_id in self.editors.keys():
                    self.original_widget = self.editors[next_mode_id]
                    self.program_status.set_result(
                        curr_mode_id, command, 'success')

                # Initialize mode
                elif next_mode_id in self.modes.keys():
                    self.original_widget = self._init_mode(next_mode_id)
                    self.program_status.set_result(
                        curr_mode_id, command, 'success')

                else:
                    self.program_status.set_result(
                        curr_mode_id, command, 'failure',
                        description=f"No such mode '{next_mode_id}'")

        # Enter default mode
        elif key == 'esc':
            self.original_widget = self.editors[DefaultMode.mode_id]

        return key

    def open_pop_up(self, force=False):
        # >>> Preliminary!
        self.set_pop_up_content(open('l.txt').read().split())
        # <<<

        left_pos = edit_pos = self.original_widget.edit_pos
        if not force:
            left_pos = self.original_widget.start_of_word_pos()
        search_str = self.original_widget.edit_text[left_pos:edit_pos]

        # Do not open pop_up if search_str has no match
        if not (force or self.auto_complete.has_match(search_str)):
            return

        self.left_string = self.original_widget.edit_text[:left_pos]
        self.right_string = self.original_widget.edit_text[edit_pos:]

        # move right part so it is not covered by pop_up
        self.original_widget.edit_text = \
            self.left_string + ' '*self.overlay_width + self.right_string

        # Set pop_up.edit_text and pop_up_parameters
        self.auto_complete.set_edit_text(search_str)
        left, top = self.get_cursor_coords(self.max_size)
        left -= len(search_str)
        self.pop_up_parameters['left'] = left
        self.pop_up_parameters['top'] = top

        super(PromptWidgetHandler, self).open_pop_up()

    def close_pop_up(self):
        self.original_widget.edit_text = \
            self.left_string + self.auto_complete.selection + self.right_string
        self.original_widget.edit_pos = \
            len(self.left_string + self.auto_complete.selection)
        return super(PromptWidgetHandler, self).close_pop_up()

    def create_pop_up(self):
        return self.auto_complete

    def get_pop_up_parameters(self):
        overlay_height = min(self.auto_complete.curr_height,
                             self.max_overlay_height)
        self.pop_up_parameters['overlay_height'] = overlay_height
        self.pop_up_parameters['overlay_width'] = self.overlay_width
        return self.pop_up_parameters

    def render(self, size, focus=False):
        self.max_size = size
        return super(PromptWidgetHandler, self).render(size, focus)

    def set_pop_up_content(self, content_list):
        self.auto_complete.set_content(content_list)
        self.overlay_width = self.auto_complete.max_width
