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
Module with the set_default_plugin_dir function which checks whether a plugin
directory has been set and if not, default to the generic one.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["set_default_plugin_dir"]

import os

from qtpy import QtCore


DEFAULT_PATH = __file__
for _ in range(4):
    DEFAULT_PATH = os.path.dirname(DEFAULT_PATH)
DEFAULT_PATH = os.path.join(DEFAULT_PATH, "pydidas_plugins")


def set_default_plugin_dir():
    _settings = QtCore.QSettings("Hereon", "pydidas")
    _val = _settings.value("global/plugin_path")
    if _val in [None, ""]:
        _settings.setValue("global/plugin_path", DEFAULT_PATH)
