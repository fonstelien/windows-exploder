import os

class ProgramStatus(object):
    status_map = {'init': "Initialized",
                  'success': "Success!",
                  'failure': "Failure!",
                  'error': "Error!",
                  'prompt': "Select option:"}

    def __init__(self, mode_id='def'):
        self.mode_id = mode_id
        self.command = ""
        self.status = 'init'
        self.description = ""
        self.presentation = ""
        self.cwd = os.getcwd()

    @property
    def parent(self):
        return os.path.dirname(self.cwd)

    @property
    def directory(self):
        return os.path.basename(self.cwd)

    def set_result(self, mode_id, command, status, description="", presentation="",
                   cwd=os.getcwd()):
        assert status in self.status_map.keys()
        self.mode_id = mode_id
        self.command = command
        self.status = status
        self.description = description.strip('\n')
        self.presentation = presentation.strip('\n')
        self.cwd = cwd

    def copy_state(self, other):
        if not other:
            return
        self.status = other.status
        self.mode_id = other.mode_id
        self.command = other.command
        self.description = other.description
        self.presentation = other.presentation
        self.cwd = other.cwd
