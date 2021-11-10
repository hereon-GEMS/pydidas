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
The dummy_loader module includes the DummyLoader class which can be used to
test workflows and Plugins without any file system operations.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['DummyLoader']

import numpy as np

from pydidas.plugins import InputPlugin, INPUT_PLUGIN
from pydidas.core import (Parameter, ParameterCollection, Dataset,
                          get_generic_parameter)

class DummyLoader(InputPlugin):
    """
    A dummy Plugin to test Input in WorkflowTrees without actual file system
    operations.
    """
    plugin_name = 'Dummy loader Plugin'
    basic_plugin = False
    plugin_type = INPUT_PLUGIN
    input_data_dim = -1
    output_data_dim = 2
    default_params = ParameterCollection(
        Parameter('image_height', int, 10, name='The image height',
                  tooltip='The height of the image.'),
        Parameter('image_width', int, 10, name='The image width',
                  tooltip='The width of the image.'),
        get_generic_parameter('filename'))

    def __init__(self, *args, **kwargs):
        InputPlugin.__init__(self, *args, **kwargs)
        self._preexecuted = False

    def __reduce__(self):
        """
        Reduce the DummyLoader for Pickling.

        Returns
        -------
        dummy_getter : callable
            The callable function to create a new instance.
        tuple
            The arguments for plugin_getter. This is only the class name.
        dict
            The state to set the state of the new object.
        """
        from .dummy_getter_ import dummy_getter
        return (dummy_getter, (self.__class__.__name__,), self.__getstate__())

    def get_first_file_size(self):
        return 1

    def pre_execute(self):
        self._preexecuted = True

    def execute(self, index, **kwargs):
        _width = self.get_param_value('image_width')
        _height =self.get_param_value('image_height')
        _data = np.random.random((_height, _width))
        _data[_data == 0] = 0.0001
        kwargs.update(dict(index=index))
        return Dataset(_data), kwargs

    def calculate_result_shape(self):
        """
        Calculate the shape of the Plugin's results.
        """
        self._config['result_shape'] = (self.get_param_value('image_height'),
                                        self.get_param_value('image_width'))
