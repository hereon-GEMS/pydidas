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
The core.constants package defines generic constants which are used
throughout the pydidas package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import __all__ items from modules:
from . import image_ops
from .colors import *
from .constants import *
from .file_extensions import *
from .gui_constants import *
from .links import *
from .main_menu_actions import *
from .main_window_menu_entries import *
from .numpy_names import *
from .paths import *
from .pyfai_names import *
from .q_settings import *
from .qt_presets import *
from .unicode_letters import *


__all__ = ["image_ops"] + (
    colors.__all__
    + constants.__all__
    + file_extensions.__all__
    + gui_constants.__all__
    + links.__all__
    + main_menu_actions.__all__
    + main_window_menu_entries.__all__
    + numpy_names.__all__
    + paths.__all__
    + pyfai_names.__all__
    + q_settings.__all__
    + qt_presets.__all__
    + unicode_letters.__all__
)

# Clean up the namespace:
del (
    colors,
    constants,
    file_extensions,
    gui_constants,
    links,
    main_menu_actions,
    main_window_menu_entries,
    numpy_names,
    paths,
    pyfai_names,
    q_settings,
    qt_presets,
    unicode_letters,
)
