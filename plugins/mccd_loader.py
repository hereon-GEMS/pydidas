from base_plugins import InputPlugin, INPUT_PLUGIN
from plugin_workflow_gui.core import Parameter

class MccdLoader(InputPlugin):
    plugin_name = 'MCCD loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    parameters = [Parameter('fname', param_type=str, default='', tooltip='The file name.'),
                  Parameter('dset', param_type=str, default='', tooltip='The dataset.'),
                  Parameter('sequence', param_type=str, default='', tooltip='The image sequence.')
                  ]
    def execute(self):
        pass
