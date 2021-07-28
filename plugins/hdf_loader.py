from pydidas.plugins import InputPlugin, INPUT_PLUGIN
from pydidas.core import Parameter
from pathlib import Path

class HdfLoader(InputPlugin):
    plugin_name = 'HDF loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    parameters = [Parameter('filename', Path, default=Path(), tooltip='The file name.'),
                  Parameter('dataset', str, default='', tooltip='The dataset.'),
                  Parameter('sequence', None, default=None, tooltip='Any acceptable image slicing sequence.')
                  ]
    input_data = []
    output_data = {0: {'name': 'image', 'dim': 2, 'labels': ['det_y', 'det_x']}}

    def execute(self, i, **kwargs):
        fname = self.get_param_value('filename')
        dset = self.get_param_value('dataset')
        seq =  self.get_param_value('sequence')
        import numpy as np
        print(f'Execute plugin {self.name} with arguments: {i}, {kwargs}')
        return np.arange((i)), {}
