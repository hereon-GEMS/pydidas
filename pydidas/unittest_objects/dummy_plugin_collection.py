# This file is part of pydidas.
#
# Copyright 2023, Helmholtz-Zentrum Hereon
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
The DummyPluginCollection module holds the DummyPluginCollection class used
for testing.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["DummyPluginCollection"]


# because these Plugins will be loaded directly by importlib, absolute imports
# are required:
from pydidas import plugins
from pydidas.plugins.plugin_collection import PluginRegistry
from pydidas.unittest_objects.create_dummy_plugins import create_plugin_class


_base_plugins = [
    plugins.BasePlugin,
    plugins.BaseFitPlugin,
    plugins.InputPlugin,
    plugins.InputPlugin1d,
    plugins.ProcPlugin,
    plugins.OutputPlugin,
]


class DummyPluginCollection(PluginRegistry):
    """
    Create a unique DummyPluginCollection with a defined path and a number
    of random plugins.
    """

    def __init__(self, **kwargs: dict):
        kwargs["plugin_path"] = kwargs.get("plugin_path", [])
        super().__init__(**kwargs)
        _nplugins = kwargs.get("n_plugins", 21)
        for num in range(_nplugins):
            _class = create_plugin_class(num % 3, number=num // 3)
            self._PluginRegistry__add_new_class(_class)
        for _plugin in _base_plugins:
            self._PluginRegistry__check_and_register_class(_plugin)
