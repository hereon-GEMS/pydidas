from base_plugins import InputPlugin, INPUT_PLUGIN

class HdfLoader(InputPlugin):
    name = 'HDF loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    ptype = 'Input plugin'
    params = {'fname': None,
              'dset': None,
              'sequence': None
              }

    def __init__(self):
        pass
