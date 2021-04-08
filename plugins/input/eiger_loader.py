from base_plugins import InputPlugin, INPUT_PLUGIN
from plugin_workflow_gui.parameter import Parameter

class EigerLoader(InputPlugin):
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    plugin_name = 'Eiger loader'
    params = {'fname': Parameter('fname', param_type=str, default='', desc='The file name.'),
              'dset': Parameter('dset', param_type=str, default='', desc='The dataset.'),
              'sequence': Parameter('sequence', param_type=str, default='', desc='The image sequence.')
              }

    def __init__(self):
        pass
