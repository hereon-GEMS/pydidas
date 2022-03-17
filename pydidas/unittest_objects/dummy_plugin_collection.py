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
The DummyPluginCollection module holds the DummyPluginCollection class used
for testing as well as the "create_plugin_class" function which can be used
to create plugin classes dynamically.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ['DummyPluginCollection']

# because these Plugins will be loaded directly by importlib, absolute imports
# are required:
from pydidas.plugins.plugin_collection import _PluginCollection
from pydidas.unittest_objects.create_dummy_plugins import create_plugin_class


class DummyPluginCollection(_PluginCollection):
    """
    Create a unique DummyPluginCollection with a defined path and a number
    of random plugins.
    """
    def __init__(self, **kwargs):
        kwargs['plugin_path'] = kwargs.get('plugin_path', [])
        super().__init__(**kwargs)
        _nplugins = kwargs.get('n_plugins', 21)
        for num in range(_nplugins):
            _class = create_plugin_class(num % 3, number=num // 3)
            self._PluginCollection__add_new_class(_class)
