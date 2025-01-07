# This file is part of pydidas.
#
# Copyright 2023 - 2025, Helmholtz-Zentrum Hereon
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
The dummy_getter_ module includes the dummy_getter function which is needed
by the __reduce__ methods of the DummyPlugins to allow pickling.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["dummy_getter"]


def dummy_getter(plugin_name: str) -> object:
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
    from pydidas.unittest_objects.dummy_loader import DummyLoader
    from pydidas.unittest_objects.dummy_proc import DummyProc
    from pydidas.unittest_objects.dummy_proc_new_dataset import DummyProcNewDataset

    if plugin_name == "DummyLoader":
        return DummyLoader()
    if plugin_name == "DummyProc":
        return DummyProc()
    if plugin_name == "DummyProcNewDataset":
        return DummyProcNewDataset()
    raise NameError(f'No DummyPlugin with the name "{plugin_name}" is known.')
