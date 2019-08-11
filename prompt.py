#!/usr/bin/env python3

import urwid
import os
import subprocess
from editor import Editor


class PromptEditor(Editor):
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
        if key == 'enter':
            self._evaluate()
        return super(PromptEditor, self).keypress(size, key)

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


class PromptWidgetHandler(urwid.WidgetPlaceholder):
    modes = {DefaultMode.mode_id: DefaultMode,
             AltMode.mode_id: AltMode}

    def __init__(self, program_status):
        self.program_status = program_status
        self.widgets = dict()
        super(PromptWidgetHandler, self).__init__(
            self._init_mode(program_status.mode_id))

    def _init_mode(self, mode_id):
        widget = self.modes[mode_id](self.program_status)
        self.widgets[mode_id] = widget
        return widget

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
                if next_mode_id in self.widgets.keys():
                    self.original_widget = self.widgets[next_mode_id]
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
            self.original_widget = self.widgets[DefaultMode.mode_id]

        return key
