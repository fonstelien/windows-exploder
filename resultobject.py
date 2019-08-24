import os


class ResultObject(object):
    status_map = {'init': "Initialized",
                  'success': "Success!",
                  'failure': "Failure!",
                  'error': "Error!",
                  'prompt': "Select option:"}

    def __init__(self):
        self.mode_id = ''
        self.command = ''
        self.status = ''
        self.description = ''
        self.presentation = ''
        self.cwd = ''

    @property
    def parent_directory(self):
        return os.path.dirname(self.cwd)

    @property
    def directory(self):
        return os.path.basename(self.cwd)

    def set_result(self, mode_id, command, status, description='',
                   presentation='', cwd=''):
        assert status in self.status_map.keys()
        self.mode_id = mode_id
        self.command = command
        self.status = status
        self.description = description.strip('\n')
        self.presentation = presentation.strip('\n')
        self.cwd = os.getcwd() if cwd == '' else cwd

    def copy_state(self, other):
        if not other:
            return
        self.status = other.status
        self.mode_id = other.mode_id
        self.command = other.command
        self.description = other.description
        self.presentation = other.presentation
        self.cwd = other.cwd