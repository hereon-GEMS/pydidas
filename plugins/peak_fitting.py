from base_plugins import ProcPlugin, PROC_PLUGIN
from plugin_workflow_gui.parameter import Parameter


class PeakFitting(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_name = 'Peak fitting'
    params = [Parameter('function', param_type=None, default=None, desc='The fit function'),
              Parameter('func_params', param_type=None, default=None, desc='The function parameters')
              ]

    def __init__(self):
        pass

    def execute(self, *data, **kwargs):
        print(f'Execute plugin {self.name} with arguments: {data}, {kwargs}')
        return data, kwargs