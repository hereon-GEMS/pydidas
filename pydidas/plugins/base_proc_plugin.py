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

"""Module with the basic processing Plugin class."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['ProcPlugin']

from pydidas.constants import PROC_PLUGIN
from .base_plugin import BasePlugin


class ProcPlugin(BasePlugin):
    """
    The base plugin class for processing plugins.
    """
    plugin_type = PROC_PLUGIN
    plugin_name = 'Base processing plugin'
    generic_params = BasePlugin.generic_params.get_copy()
    default_params = BasePlugin.default_params.get_copy()
