from base_plugins import ProcPlugin, PROC_PLUGIN

class PeakFitting(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    name = 'Peak fitting'
    ptype = 'Processing plugin'
    params = {'function': None,
              'bg_correction': None,
              }

    def __init__(self):
        pass

    def execute(self, *data, **kwargs):
        print(f'Execute plugin {self.name} with arguments: {data}, {kwargs}')
        return data, kwargs