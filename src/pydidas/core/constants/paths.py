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
Module with paths which are used throughout the pydidas package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = [
    "PYDIDAS_CONFIG_PATHS",
    "PYDIDAS_STANDARD_CONFIG_PATH",
    "GENERIC_PLUGIN_PATH",
]


from pathlib import Path

from qtpy import QtCore


PYDIDAS_CONFIG_PATHS = []

for _path in QtCore.QStandardPaths.standardLocations(
    QtCore.QStandardPaths.ConfigLocation
):
    _config_path = Path(_path)
    if not _config_path.stem == "pydidas":
        if not _config_path.stem == "Hereon":
            _config_path = _config_path.joinpath("Hereon")
        _config_path = _config_path.joinpath("pydidas")
    PYDIDAS_CONFIG_PATHS.append(_config_path)

PYDIDAS_STANDARD_CONFIG_PATH = PYDIDAS_CONFIG_PATHS[0]

GENERIC_PLUGIN_PATH = (
    Path(__file__).absolute().parent.parent.parent.parent.joinpath("pydidas_plugins")
)
