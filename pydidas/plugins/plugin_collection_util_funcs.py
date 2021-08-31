# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""
Module with the utility functions called by the PluginCollection class.
"""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['get_generic_plugin_path', 'plugin_type_check',
           'plugin_consistency_check']


import os

from .plugin_constants import INPUT_PLUGIN, PROC_PLUGIN, OUTPUT_PLUGIN


def get_generic_plugin_path():
    """
    Get the generic plugin path.

    By default, plugins will be put in the pydidas/plugins folder whereas
    the code is located in the pydidas/pydidas folder.

    Returns
    -------
    str
        The path to the generic plugin folder.
    """
    return [os.path.join(
        os.path.dirname(
        os.path.dirname(
        os.path.dirname(__file__))), 'plugins')]


def plugin_type_check(cls_item):
    """
    TO DO
    """
    if cls_item.basic_plugin:
        return -1
    return cls_item.plugin_type
    raise ValueError('Could not determine the plugin type for'
                     'class "{cls_item.__name__}"')


def plugin_consistency_check(cls_item):
    """
    Verify that plugins pass a rudimentary sanity check.

    Parameters
    ----------
    cls_item : plugin object
        A plugin class.

    Returns
    -------
    bool.
        Returns True if consistency check succeeded and False otherwise.
    """
    return (getattr(cls_item, '_is_pydidas_plugin', False)
            and not getattr(cls_item, 'basic_plugin', True))
