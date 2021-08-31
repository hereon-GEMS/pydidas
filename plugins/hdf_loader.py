from pydidas.plugins import InputPlugin, INPUT_PLUGIN
from pydidas.core import Parameter, ParameterCollection, get_generic_parameter
from pathlib import Path

class HdfLoader(InputPlugin):
    plugin_name = 'HDF loader'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    default_params = ParameterCollection(
    Parameter('Filename', Path, default=Path(), tooltip='The file name.',
              refkey=''),
    get_generic_parameter('hdf5_key'))
    input_data = None
    output_data_dim = 2

    def execute(self, i, **kwargs):
        fname = self.get_param_value('filename')
        dset = self.get_param_value('dataset')
        import numpy as np
        print(f'Execute plugin {self.name} with arguments: {i}, {kwargs}')
        return np.arange((i)), {}
