from pydidas.plugins import ProcPlugin, PROC_PLUGIN
from pydidas.core import Parameter, ParameterCollection

import numpy as np

class DummyProc(ProcPlugin):
    plugin_name = 'Dummy loader Plugin'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    input_data = []
    output_data = {0: {'name': 'image', 'dim': 2, 'labels': ['det_y', 'det_x']}}
    default_params = ParameterCollection()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, data, **kwargs):
        _offset = np.random.random()
        _data = data + _offset
        kwargs.update({f'offset_{self.node_id:02d}': _offset})
        return _data, kwargs
