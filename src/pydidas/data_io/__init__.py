# This file is part of pydidas.
#
# Copyright 2023 - 2024, Helmholtz-Zentrum Hereon
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
The data_io subpackage includes functionality to load and save data in
various formats.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []

# import sub-packages:
from . import implementations
from . import low_level_readers
from . import utils

# import __all__ items from modules:

from .import_export import *
from .io_manager import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import import_export

__all__.extend(import_export.__all__)
del import_export

from . import io_manager

__all__.extend(io_manager.__all__)
del io_manager
