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
The pydidas.workflow.processing_tree_io package includes importers/exporters for the
WorkflowTree in different formats as well as a registry metaclass to handle actual
imports/exports.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import __all__ items from modules:
from .processing_tree_io_base import *
from .processing_tree_io_meta import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import processing_tree_io_base

__all__.extend(processing_tree_io_base.__all__)
del processing_tree_io_base

from . import processing_tree_io_meta

__all__.extend(processing_tree_io_meta.__all__)
del processing_tree_io_meta

# Automatically find and import IO classes to have them registered
# with the Metaclass:
from pathlib import Path as __Path
import importlib as __importlib

_dir = __Path(__file__).parent
__io_classes = set(
    item.stem
    for item in _dir.iterdir()
    if (
        item.is_file()
        and item.name.startswith("processing_tree_io")
        and not any(item.name.endswith(_suffix) for _suffix in ["base.py", "meta.py"])
    )
)

for __module in __io_classes:
    __pymodule = __importlib.import_module(f".{__module}", __package__)
    __all__ += __pymodule.__all__

del __pymodule
