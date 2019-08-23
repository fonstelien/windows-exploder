#!/usr/bin/env python3

import urwid
import os
import subprocess
import re

import editor
import dropdown


class PromptEditor(editor.Editor):
    mode_id = '---'
    eval_pattern = re.compile(r'(?:\s*)(\w+)(?:\s*)(.*)', flags=re.UNICODE)

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

    def get_standard_presentation(self):
        subproc = subprocess.run(
            "ls -lp | grep -v /$ ; tree -L 2 -dD",
            shell=True, capture_output=True, encoding='UTF-8')
        return subproc.stdout

    def _evaluate(self):
        match = self.eval_pattern.match(self.edit_text)

        # List cwd contents
        if not match:
            if self.edit_text != '':  # _evaluate() in sub class
                return False

            self.program_status.set_result(
                self.mode_id, self.edit_text, 'success',
                presentation=self.get_standard_presentation())
            return True

        op, args = match.groups()

        # Change mode
        if op == 'mode':
            if args:
                # Rest is handled by PromptWidgetHandler
                self.change_mode = args
            else:
                self.program_status.set_result(
                    self.mode_id, self.edit_text, 'failure',
                    description="mode: missing argument")
            return True

        # Change directory
        if op == 'cd':
            self.change_directory(args)
            return True

        # Run bash command
        if op == 'sh':
            self.run_bash_command(args)
            return True

        # Open file
        if op == 'clk':
            self.open_file(args)
            return True

        # Start application
        if op == 'app':
            self.start_application(args)
            return True

        return False

    def run_bash_command(self, cmd):
        def expand_alias(match):
            if not match:
                return None
            if 'll' in match.groups():
                return 'ls -alF'
            if 'la' in match.groups():
                return 'ls -Ap'
            if 'l' in match.groups():
                return 'ls -Fp'
            if 'g' in match.groups():
                return 'grep'
            if 'kll' in match.groups():
                return 'pkill'
            return None

        def add_colors(match):
            if not match:
                return None
            if 'tree' in match.groups():
                return 'tree -C'
            if 'ls' in match.groups():
                return 'ls --color=always'
            if 'grep' in match.groups():
                return 'grep --color=always'
            return None

        alias_patterns = [
            r'l[la]+',  # ls
            r'g',       # grep
            r'kll',     # pkill
        ]

        for ptrn in alias_patterns:
            cmd = re.sub(
                fr'((^{ptrn})(?!\S))|((?<=[|&;]\s)(?:\s*)({ptrn})(?!\S))',
                expand_alias, cmd)

        color_patterns = [r'tree', r'ls', r'grep']

        for ptrn in color_patterns:
            without_pipe = fr'((^{ptrn})(?!\S)(?!.*\|))'
            with_pipe = fr'((?<=[|&;]\s)(?:\s*)({ptrn})(?!\S))'
            cmd = re.sub(fr'{without_pipe}|{with_pipe}',
                         add_colors, cmd)

        subproc = subprocess.run(
            cmd, shell=True, capture_output=True, encoding='UTF-8')
        if subproc.returncode == 0:
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'success',
                presentation=subproc.stdout)
        else:
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'failure',
                description=subproc.stderr)

    def open_file(self, filename):
        """Open file 'filename' in default application"""
        args = ['xdg-open', filename]
        pipe = subprocess.PIPE
        subproc = subprocess.Popen(
            args, encoding='UTF-8', stdout=pipe, stderr=pipe)

        try:
            outs, errs = subproc.communicate(timeout=1)
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'failure', description=errs)

        except subprocess.TimeoutExpired:
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'success')

    def start_application(self, app_name):
        """Starts the program 'app_name'"""
        pipe = subprocess.PIPE
        subproc = subprocess.Popen(
            app_name, encoding='UTF-8', stdout=pipe, stderr=pipe)

        try:
            outs, errs = subproc.communicate(timeout=1)
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'failure', description=errs)

        except subprocess.TimeoutExpired:
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'success')

    def change_directory(self, path):
        if path == '':
            path = os.path.expanduser('~')
        try:
            os.chdir(path)
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'success',
                presentation=self.get_standard_presentation())
        except FileNotFoundError:
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'failure',
                description=f"No such file or directory: '{path}'")
        except NotADirectoryError:
            self.program_status.set_result(
                self.mode_id, self.edit_text, 'failure',
                description=f"Not a directory: '{path}'")


class DefaultMode(PromptEditor):
    mode_id = 'dir'

    def keypress(self, size, key):
        super(DefaultMode, self).keypress(size, key)
        if key == 'enter':
            self._evaluate()

        return key

    def _evaluate(self):
        if super(DefaultMode, self)._evaluate():
            return True
        path = self.edit_text
        if os.path.isfile(path):
            self.open_file(path)
        else:
            self.change_directory(path)
        return True


class BashMode(PromptEditor):
    mode_id = 'bsh'

    def keypress(self, size, key):
        super(BashMode, self).keypress(size, key)
        if key == 'enter':
            self._evaluate()

        return key

    def _evaluate(self):
        if super(BashMode, self)._evaluate():
            return True
        self.run_bash_command(self.edit_text)
        return True


class PromptWidgetHandler(urwid.PopUpLauncher):
    modes = {DefaultMode.mode_id: DefaultMode,
             BashMode.mode_id: BashMode}

    def __init__(self, program_status):
        self.pop_up = dropdown.DropDown()
        urwid.connect_signal(
            self.pop_up, 'close', lambda x: self.close_pop_up())
        urwid.connect_signal(
            self.pop_up, 'render', lambda x: self._invalidate())

        self.editor_status = ('', 0)  # (edit_text, edit_pos)

        # pop_up dimensionging and placement
        self.pop_up_parameters = {
            'left': 0, 'top': 0, 'overlay_height': 0, 'overlay_width': 0}
        self.max_overlay_height = 8
        self.min_overlay_width = 13
        self.overlay_width = 1
        self.max_size = None  # (maxcol,) -- the size parameter to render()

        self.program_status = program_status
        self.editors = dict()
        super(PromptWidgetHandler, self).__init__(
            self._init_mode(program_status.mode_id))

    def _init_mode(self, mode_id):
        editor = self.modes[mode_id](self.program_status)
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

        # Change mode
        if key == 'enter':
            if self.original_widget.change_mode:
                curr_mode_id = self.original_widget.mode_id
                next_mode_id = self.original_widget.change_mode
                command = self.original_widget.edit_text

                # Load previously used mode
                if next_mode_id in self.editors.keys():
                    self.original_widget = self.editors[next_mode_id]
                    self.program_status.set_result(
                        curr_mode_id, command, 'success')

                # Initialize mode
                elif next_mode_id in self.modes.keys():
                    self.original_widget = self._init_mode(next_mode_id)
                    self.program_status.set_result(
                        curr_mode_id, command, 'success')

                # Undefined mode
                else:
                    self.program_status.set_result(
                        curr_mode_id, command, 'failure',
                        description=f"No such mode '{next_mode_id}'")

            return key

        # Enter default mode
        if key == 'esc':
            self.original_widget = self.editors[DefaultMode.mode_id]
            return key

        editor = self.original_widget

        # Auto complete the '.' and '..' for current and parent directories
        if re.match(r'(.*\s)?\.{1,2}\Z', editor.edit_text[:editor.edit_pos]):
            if key == 'tab':
                self.original_widget.insert_text('/')
            return key

        # Open auto_complete pop up
        if (len(key) == 1 or key in editor._deleters) and \
           (editor.edit_pos - editor.start_of_word_pos()) > 1:
            self.open_pop_up(force=False)
        elif key == 'tab':
            self.open_pop_up(force=True)

        return key

    def open_pop_up(self, force=False):
        self.set_pop_up_content()
        if not self.pop_up.selectable():
            return

        edit_text = self.original_widget.edit_text
        edit_pos = self.original_widget.edit_pos
        search_str = re.match(r'(?:.*\W)?(\w*\Z)',
                              edit_text[:edit_pos]).group(1)
        left_pos = edit_pos - len(search_str)

        # # Do not open pop_up if search_str has no match
        if not (force or self.pop_up.has_match(search_str)):
            return

        # Set auto_complete.edit_text and pop_up_parameters
        self.pop_up.set_edit_text(search_str)
        left, top = self.get_cursor_coords(self.max_size)
        left -= len(search_str)
        overlay_width = max(self.overlay_width, self.min_overlay_width)
        self.pop_up_parameters['left'] = left
        self.pop_up_parameters['top'] = top
        self.pop_up_parameters['overlay_width'] = overlay_width

        # Make Editor.edit_text ready for the auto_complete pop up
        edit_text = edit_text[:left_pos] + edit_text[edit_pos:]
        self.original_widget.edit_text = edit_text  # Remove search_str
        self.original_widget.edit_pos = left_pos
        self.editor_status = (edit_text, left_pos)  # Restore in close_pop_up()
        self.original_widget.insert_text(' '*self.overlay_width)

        super(PromptWidgetHandler, self).open_pop_up()

    def close_pop_up(self):
        self.original_widget.edit_text, self.original_widget.edit_pos = \
            self.editor_status
        self.original_widget.insert_text(self.pop_up.selection)
        return super(PromptWidgetHandler, self).close_pop_up()

    def create_pop_up(self):
        return self.pop_up

    def get_pop_up_parameters(self):
        overlay_height = min(self.pop_up.curr_height,
                             self.max_overlay_height)
        self.pop_up_parameters['overlay_height'] = overlay_height
        return self.pop_up_parameters

    def render(self, size, focus=False):
        self.max_size = size
        return super(PromptWidgetHandler, self).render(size, focus)

    def set_pop_up_content(self):
        """Set auto complete content"""

        def list_directory_contents(path):
            if not os.path.isdir(path):
                return list()
            _, dirs, files = next(os.walk(path))
            dirs = [d+'/' for d in dirs]
            return dirs + files

        editor = self.original_widget
        keyword = editor.edit_text
        if keyword != '':
            keyword = keyword[:editor.edit_pos]
        content_list = list()

        if re.match('(mode ).*', keyword):
            content_list = self.modes.keys()

        # DefaultMode active
        elif editor.mode_id == DefaultMode.mode_id:
            path = os.path.join(os.getcwd(), keyword)
            dirname, basename = os.path.split(path)
            content_list = list_directory_contents(dirname)

        self.pop_up.set_content(content_list)
        self.overlay_width = self.pop_up.max_width
