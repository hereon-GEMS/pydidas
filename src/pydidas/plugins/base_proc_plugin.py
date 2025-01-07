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
Module with the ProcPlugin base class.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["ProcPlugin"]


from pydidas.core.constants import PROC_PLUGIN, PROC_PLUGIN_GENERIC
from pydidas.plugins.base_plugin import BasePlugin


class ProcPlugin(BasePlugin):
    """
    The base plugin class for processing plugins.

    This class updates the "plugin_type" and "plugin_subtype" attributes.
    """

    plugin_type = PROC_PLUGIN
    plugin_subtype = PROC_PLUGIN_GENERIC
    plugin_name = "Base processing plugin"
    generic_params = BasePlugin.generic_params.copy()
    default_params = BasePlugin.default_params.copy()


ProcPlugin.register_as_base_class()
