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
Module with the LocalPluginCollection class which allows to test plugins locally
without setting the global QSettings.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["LocalPluginCollection"]


from pathlib import Path

import pydidas
from pydidas.plugins.plugin_registry import PluginRegistry


class LocalPluginCollection(PluginRegistry):
    """
    The LocalPluginCollection is a PluginRegistry for unittests.

    It includes predetermined local paths (relative to this file) and a
    "testing" QSetting registry key.
    """

    def __init__(self, *args: tuple, **kwargs: dict):
        kwargs["plugin_path"] = [
            Path(pydidas.__file__).parent.parent.joinpath("pydidas_plugins"),
            Path(pydidas.__file__).parent.joinpath("unittest_objects"),
        ]
        PluginRegistry.__init__(self, *args, **kwargs)
        self.q_settings_version = "unittesting"
