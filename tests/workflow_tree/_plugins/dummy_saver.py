from pydidas.plugins import OutputPlugin, OUTPUT_PLUGIN
from pydidas.core import Parameter, ParameterCollection

import numpy as np

class DummySaver(OutputPlugin):
    plugin_name = 'Dummy loader Plugin'
    basic_plugin = False
    plugin_type = OUTPUT_PLUGIN
    input_data = []
    output_data = {0: {'name': 'image', 'dim': 2, 'labels': ['det_y', 'det_x']}}
    default_params = ParameterCollection()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, data, **kwargs):
        _offset = np.random.random()
        _data = data + _offset
        _key = f'offset_{self.node_id:02d}'
        return _data, kwargs.update({_key: _offset})
