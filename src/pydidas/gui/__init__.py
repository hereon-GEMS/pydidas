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
Subpackage with GUI element and managers to access all of pydidas's
functionality from within a graphical user interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import subpackages
from . import frames
from . import managers
from . import mixins

__all__.extend(["frames", "managers", "mixins"])

# import __all__ items from modules:
from .gui_excepthook_ import *
from .main_window import *
from .start_pydidas_gui import *


# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import gui_excepthook_

__all__.extend(gui_excepthook_.__all__)
del gui_excepthook_

from . import main_window

__all__.extend(main_window.__all__)
del main_window
