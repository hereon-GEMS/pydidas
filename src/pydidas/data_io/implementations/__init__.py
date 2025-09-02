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
The data__io.implementations package includes imports/exporters for data
in different formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


import importlib as __importlib
import pathlib as __pathlib

from .io_base import *


__all__ = io_base.__all__

for _item in __pathlib.Path(__file__).parent.iterdir():
    if (
        _item.is_file()
        and _item.suffix == ".py"
        and _item.stem not in ("__init__", "io_base")
    ):
        __importlib.import_module(
            "pydidas.data_io.implementations." + _item.stem, __package__
        )
