from base_plugins import InputPlugin, INPUT_PLUGIN
from plugin_workflow_gui.parameter import Parameter

class HdfLoader(InputPlugin):
    plugin_name = 'HDF loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    params = [Parameter('fname', param_type=str, default='', desc='The file name.'),
              Parameter('dset', param_type=str, default='', desc='The dataset.'),
              Parameter('sequence', param_type=str, default='', desc='The image sequence.')
              ]
    input_data = []
    output_data = {0: {'name': 'image', 'dim': 2, 'labels': ['det_y', 'det_x']}}

    def __init__(self):
        super().__init__()

    def execute(self, i, **kwargs):
        import numpy as np
        print(f'Execute plugin {self.name} with arguments: {i}, {kwargs}')
        return np.arange((i)), {}