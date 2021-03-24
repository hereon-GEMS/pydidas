from base_plugins import InputPlugin, INPUT_PLUGIN

class HdfLoader(InputPlugin):
    plugin_name = 'HDF loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    params = {'fname': None,
              'dset': None,
              'sequence': None
              }

    def __init__(self):
        super().__init__()

    def execute(self, i, **kwargs):
        import numpy as np
        print(f'Execute plugin {self.name} with arguments: {i}, {kwargs}')
        return np.arange((i)), {}