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
