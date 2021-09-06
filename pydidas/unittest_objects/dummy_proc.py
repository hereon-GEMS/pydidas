from pydidas.plugins import ProcPlugin, PROC_PLUGIN
from pydidas.core import Parameter, ParameterCollection

import numpy as np

class DummyProc(ProcPlugin):
    plugin_name = 'Dummy processing Plugin'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    input_data_dim = -1
    output_data = -1
    default_params = ParameterCollection()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preexecuted = False

    def execute(self, data, **kwargs):
        _offset = np.random.random()
        _data = data + _offset
        kwargs.update({f'offset_{self.node_id:02d}': _offset})
        return _data, kwargs

    def pre_execute(self):
        self._preexecuted = True
