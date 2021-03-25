from base_plugins import ProcPlugin, PROC_PLUGIN
from plugin_workflow_gui.parameter import Parameter

class BackgroundCorrection(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_name = 'Background correction'
    params = {'function': None,
              'params': None,
              }

    def __init__(self):
        pass

    def execute(self, *data, **kwargs):
        print(f'Execute plugin {self.name} with arguments: {data}, {kwargs}')
        for _data in data:
            _data -= 1
        return data, kwargs

