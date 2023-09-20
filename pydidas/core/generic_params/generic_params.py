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
The generic_params module holds the dictionary with information required for creating
generic Parameters.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = ["GENERIC_PARAMS_METADATA"]


import importlib
from collections import ChainMap
from pathlib import Path


_prefix = "pydidas.core.generic_params."

GENERIC_PARAMS_METADATA = dict(
    ChainMap(
        *[
            getattr(
                importlib.import_module(_prefix + _module_name, __package__),
                _module_name.upper(),
            )
            for _module_name in [
                _object.stem
                for _object in Path(__file__).parent.iterdir()
                if _object.name.startswith("generic_params_")
            ]
        ]
    )
)
