from pydidas.plugins import InputPlugin, INPUT_PLUGIN
from pydidas.core import Parameter

class EigerLoader(InputPlugin):
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    plugin_name = 'Eiger loader'
    parameters = [Parameter('fname', param_type=str, default='', tooltip='The file name.'),
                  Parameter('dset', param_type=str, default='', tooltip='The dataset.'),
                  Parameter('sequence', param_type=str, default='', tooltip='The image sequence.')
                  ]

    def __init__(self):
        InputPlugin.__init__(self)

    def execute(self):
        pass
