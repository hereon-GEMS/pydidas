from base_plugins import InputPlugin, INPUT_PLUGIN
from plugin_workflow_gui.parameter import Parameter

class MccdLoader(InputPlugin):
    plugin_name = 'MCCD loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    params = [Parameter('fname', param_type=str, default='', desc='The file name.'),
              Parameter('dset', param_type=str, default='', desc='The dataset.'),
              Parameter('sequence', param_type=str, default='', desc='The image sequence.')
              ]
    def __init__(self):
        pass
