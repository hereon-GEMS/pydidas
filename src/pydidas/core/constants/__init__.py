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
The core.constants package defines generic constants which are used
throughout the pydidas package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2024, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"
__all__ = []


# import __all__ items from modules:
from .colors import *
from .constants import *
from .file_extensions import *
from .gui_constants import *
from .links import *
from .main_menu_actions import *
from .numpy_names import *
from .paths import *
from .pyfai_names import *
from .q_settings import *
from .qt_presets import *
from .unicode_letters import *

from . import image_ops

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import colors

__all__.extend(colors.__all__)
del colors

from . import constants

__all__.extend(constants.__all__)
del constants

from . import file_extensions

__all__.extend(file_extensions.__all__)
del file_extensions

from . import gui_constants

__all__.extend(gui_constants.__all__)
del gui_constants

from . import links

__all__.extend(links.__all__)
del links

from . import main_menu_actions

__all__.extend(main_menu_actions.__all__)
del main_menu_actions

from . import numpy_names

__all__.extend(numpy_names.__all__)
del numpy_names

from . import paths

__all__.extend(paths.__all__)
del paths

from . import pyfai_names

__all__.extend(pyfai_names.__all__)
del pyfai_names

from . import q_settings

__all__.extend(q_settings.__all__)
del q_settings

from . import qt_presets

__all__.extend(qt_presets.__all__)
del qt_presets

from . import unicode_letters

__all__.extend(unicode_letters.__all__)
del unicode_letters
