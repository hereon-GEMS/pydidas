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
Module with the set_default_plugin_dir function which checks whether a plugin
directory has been set and if not, default to the generic one.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["set_default_plugin_dir"]


import os

from ..pydidas_q_settings import PydidasQsettings


DEFAULT_PATH = __file__
for _ in range(4):
    DEFAULT_PATH = os.path.dirname(DEFAULT_PATH)
DEFAULT_PATH = os.path.join(DEFAULT_PATH, "pydidas_plugins")


def set_default_plugin_dir():
    """
    Set the default plugin directory if no plugin directory has been defined.

    The function looks at the QSettings at the time of the function call.
    """
    _settings = PydidasQsettings()
    _val = _settings.value("user/plugin_path")
    if _val in [None, ""]:
        _settings.set_value("user/plugin_path", DEFAULT_PATH)
