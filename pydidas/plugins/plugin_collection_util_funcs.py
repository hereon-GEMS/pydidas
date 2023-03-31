# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Module with the utility functions called by the PluginCollection class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = ["get_generic_plugin_path", "plugin_type_check"]

from pathlib import Path

from .. import core
from ..core.utils import LOGGING_LEVEL, pydidas_logger

logger = pydidas_logger(LOGGING_LEVEL)


def get_generic_plugin_path():
    """
    Get the generic plugin path.

    By default, plugins will be put in the pydidas/plugins folder whereas
    the code is located in the pydidas/pydidas folder.

    Returns
    -------
    list
        A list with the path to the generic plugin folder as the only entry.
    """
    _pydidas_module_path = Path(core.__path__[0]).absolute().parent.parent
    return [_pydidas_module_path.joinpath("pydidas_plugins")]


def plugin_type_check(cls_item):
    """
    Check the type of the Plugin (input, processing, output).

    Returns
    -------
    int
        The integer code for the Plugin type.
    """
    if cls_item.basic_plugin:
        return -1
    return cls_item.plugin_type
