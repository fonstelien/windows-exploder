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
    def parent_exec_wd(self):
        return os.path.dirname(self.exec_wd)

    @property
    def base_exec_wd(self):
        return os.path.basename(self.exec_wd)

    def set_result(self, mode_id, command, status, description='',
                   presentation='', exec_wd=''):
        assert status in self.status_map.keys()
        self.mode_id = mode_id
        self.command = command
        self.status = status
        self.description = description.strip('\n')
        self.presentation = presentation.strip('\n')
        self.exec_wd = os.getcwd() if exec_wd == '' else exec_wd

    def copy_state(self, other):
        if not other:
            return
        self.status = other.status
        self.mode_id = other.mode_id
        self.command = other.command
        self.description = other.description
        self.presentation = other.presentation
        self.exec_wd = other.exec_wd
