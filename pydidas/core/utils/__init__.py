# This file is part of pydidas.
#
# Copyright 2021-, Helmholtz-Zentrum Hereon
# SPDX-License-Identifier: GPL-3.0-only
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The core.utils sub-package provides generic convenience functions and classes
which are used throughout the package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .clipboard_ import *
from .decorators import *
from .file_checks import *
from .file_utils import *
from .iterable_utils import *
from .format_arguments_ import *
from .get_documentation_targets import *
from .get_pydidas_icons import *
from .hdf5_dataset_utils import *
from .logger import *
from .math_utils import *
from .no_print import *
from .qt_utilities import *
from .rebin_ import *
from .set_default_plugin_dir_ import *
from .show_busy_mouse import *
from .signal_blocker import *
from .sphinx_html import *
from .str_utils import *
from .timer import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import clipboard_

__all__.extend(clipboard_.__all__)
del clipboard_

from . import decorators

__all__.extend(decorators.__all__)
del decorators

from . import file_checks

__all__.extend(file_checks.__all__)
del file_checks

from . import file_utils

__all__.extend(file_utils.__all__)
del file_utils

from . import format_arguments_

__all__.extend(format_arguments_.__all__)
del format_arguments_

from . import get_documentation_targets

__all__.extend(get_documentation_targets.__all__)
del get_documentation_targets

from . import get_pydidas_icons

__all__.extend(get_pydidas_icons.__all__)
del get_pydidas_icons

from . import hdf5_dataset_utils

__all__.extend(hdf5_dataset_utils.__all__)
del hdf5_dataset_utils

from . import iterable_utils

__all__.extend(iterable_utils.__all__)
del iterable_utils

from . import logger

__all__.extend(logger.__all__)
del logger

from . import math_utils

__all__.extend(math_utils.__all__)
del math_utils

from . import no_print

__all__.extend(no_print.__all__)
del no_print

from . import qt_utilities

__all__.extend(qt_utilities.__all__)
del qt_utilities

from . import rebin_

__all__.extend(rebin_.__all__)
del rebin_

from . import set_default_plugin_dir_

__all__.extend(set_default_plugin_dir_.__all__)
del set_default_plugin_dir_

from . import show_busy_mouse

__all__.extend(show_busy_mouse.__all__)
del show_busy_mouse

from . import signal_blocker

__all__.extend(signal_blocker.__all__)
del signal_blocker

from . import sphinx_html

__all__.extend(sphinx_html.__all__)
del sphinx_html

from . import str_utils

__all__.extend(str_utils.__all__)
del str_utils

from . import timer

__all__.extend(timer.__all__)
del timer
