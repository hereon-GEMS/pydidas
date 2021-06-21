from base_plugins import ProcPlugin, PROC_PLUGIN
from pydidas.core import Parameter

class BackgroundCorrection(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_name = 'Background correction'
    parameters = [Parameter('function', param_type=None, default=None, tooltip='The background correction function'),
                  Parameter('function params', param_type=None, default=None, tooltip='Calling parameters for the fit function')
                  ]

    def execute(self, *data, **kwargs):
        print(f'Execute plugin {self.name} with arguments: {data}, {kwargs}')
        for _data in data:
            _data -= 1
        return data, kwargs

