# This file is part of pydidas.
#
# Copyright 2023 - 2026, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
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
__copyright__ = "Copyright 2023 - 2026, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["plugin_getter"]


from typing import TYPE_CHECKING

from pydidas.plugins.plugin_collection import PluginCollection


COLL = PluginCollection()


if TYPE_CHECKING:
    from pydidas.plugins.base_plugin import BasePlugin


def plugin_getter(plugin_name: str) -> "BasePlugin":
    """
    Get a new Plugin instance from a Plugin name.

    Parameters
    ----------
    plugin_name : str
        The Plugin class name.

    Returns
    -------
    plugin : BasePlugin
        The new Plugin instance.
    """
    plugin = COLL.get_plugin_by_name(plugin_name)
    return plugin()
