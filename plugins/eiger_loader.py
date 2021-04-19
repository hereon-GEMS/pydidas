from base_plugins import InputPlugin, INPUT_PLUGIN
from plugin_workflow_gui.parameter import Parameter

class EigerLoader(InputPlugin):
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    plugin_name = 'Eiger loader'
    parameters = [Parameter('fname', param_type=str, default='', tooltip='The file name.'),
                  Parameter('dset', param_type=str, default='', tooltip='The dataset.'),
                  Parameter('sequence', param_type=str, default='', tooltip='The image sequence.')
                  ]

    def execute(self):
        pass
