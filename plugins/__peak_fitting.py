from base_plugins import ProcPlugin, PROC_PLUGIN
from plugin_workflow_gui.parameter import Parameter


class uuPeakFitting(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    plugin_name = 'uu Peak fitting'
    parameters = [Parameter('function', param_type=None, default=None, tooltip='The fit function', choices=['Func 1', 'Func 2', 'Func 3']),
                  Parameter('func_params', param_type=None, default=None, tooltip='The function parameters')
                  ]

    def execute(self, *data, **kwargs):
        print(f'Execute plugin {self.name} with arguments: {data}, {kwargs}')
        return data, kwargs