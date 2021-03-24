from base_plugins import InputPlugin, INPUT_PLUGIN

class EigerLoader(InputPlugin):
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    plugin_name = 'Eiger loader'
    params = {'fname': None,
              'dset': None,
              'sequence': None
              }

    def __init__(self):
        pass
