# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The dummy_proc module includes the DummyProc class which can be used to
test workflows and Plugins without any file system operations.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['DummyProc']

from pydidas.plugins import ProcPlugin, PROC_PLUGIN
from pydidas.core import ParameterCollection, Dataset

import numpy as np

class DummyProc(ProcPlugin):
    plugin_name = 'Dummy processing Plugin'
    basic_plugin = False
    plugin_type = PROC_PLUGIN
    input_data_dim = -1
    output_data_dim = -1
    default_params = ParameterCollection()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preexecuted = False
        self._executed = False

    def execute(self, data, **kwargs):
        self._executed = True
        _offset = kwargs.get('offset', np.random.random())
        _data = Dataset(data + _offset)
        kwargs.update({f'offset_{self.node_id:02d}': _offset})
        return _data, kwargs

    def pre_execute(self):
        self._preexecuted = True
