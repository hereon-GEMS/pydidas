# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the plugin_getter function which can be used to get a Plugin
from the PluginCollection by its plugin_name attribute. This function is
required to allow pickling of Plugins.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['plugin_getter']

from .plugin_collection import PluginCollection


COLL = PluginCollection()


def plugin_getter(plugin_name):
    """
    Get a new Plugin instance from a Plugin name.

    Parameters
    ----------
    plugin_name : str
        The Plugin class name.

    Returns
    -------
    plugin : pydidas.plugins.BasePlugin
        The new Plugin instance.
    """
    plugin = COLL.get_plugin_by_name(plugin_name)
    return plugin()
