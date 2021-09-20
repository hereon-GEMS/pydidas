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

"""Module with the GlobalSettings class which is used to manage global
information independant from the individual frames."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ScanSettings']

from .generic_parameters import get_generic_parameter
from .parameter_collection import ParameterCollection
from .object_with_parameter_collection import ObjectWithParameterCollection
from .singleton_factory import SingletonFactory


DEFAULT_PARAMS = ParameterCollection(
    get_generic_parameter('scan_dim'),
    get_generic_parameter('scan_dir_1'),
    get_generic_parameter('scan_dir_2'),
    get_generic_parameter('scan_dir_3'),
    get_generic_parameter('scan_dir_4'),
    get_generic_parameter('n_points_1'),
    get_generic_parameter('n_points_2'),
    get_generic_parameter('n_points_3'),
    get_generic_parameter('n_points_4'),
    get_generic_parameter('delta_1'),
    get_generic_parameter('delta_2'),
    get_generic_parameter('delta_3'),
    get_generic_parameter('delta_4'),
    get_generic_parameter('unit_1'),
    get_generic_parameter('unit_2'),
    get_generic_parameter('unit_3'),
    get_generic_parameter('unit_4'),
    get_generic_parameter('offset_1'),
    get_generic_parameter('offset_2'),
    get_generic_parameter('offset_3'),
    get_generic_parameter('offset_4'),
    )


class _ScanSettings(ObjectWithParameterCollection):
    """
    Class which holds experimental settings. This class must only be
    instanciated through its factory, therefore guaranteeing that only a
    single instance exists.
    """
    default_params = DEFAULT_PARAMS

    def __init__(self, *args, **kwargs):
        """Setup method"""
        super().__init__()
        self.set_default_params()


ScanSettings = SingletonFactory(_ScanSettings)
