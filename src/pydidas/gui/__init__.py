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
Subpackage with GUI element and managers to access all of pydidas's
functionality from within a graphical user interface.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import subpackages
from . import frames, managers, mixins

# import items from modules:
from .gui_excepthook_ import *
from .main_window import *
from .start_pydidas_gui_ import *


__all__ = ["frames", "managers", "mixins"] + (
    gui_excepthook_.__all__ + main_window.__all__ + start_pydidas_gui_.__all__
)

del gui_excepthook_, main_window, start_pydidas_gui_
