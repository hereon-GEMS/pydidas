from base_plugins import InputPlugin, INPUT_PLUGIN

class MccdLoader(InputPlugin):
    plugin_name = 'MCCD loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    params = {'fname': None,
              'dset': None,
              'sequence': None
              }

    def __init__(self):
        pass
