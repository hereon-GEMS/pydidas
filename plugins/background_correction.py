from base_plugins import ProcPlugin, PROC_PLUGIN

class BackgroundCorrection(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    name = 'Background correction'
    ptype = 'Processing plugin'
    params = {'function': None,
              'params': None,
              }

    def __init__(self):
        pass
