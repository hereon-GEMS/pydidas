from base_plugins import ProcPlugin, PROC_PLUGIN

class AzimuthalIntegration(ProcPlugin):
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    name = 'Azimuthal integration'
    ptype = 'Processing plugin'
    params = {'beam_cente_x': None,
              'beam_cente_y': None,
              'bins': None,
              'theta_min': None,
              'theta_max': None,
              }

    def __init__(self):
        pass
