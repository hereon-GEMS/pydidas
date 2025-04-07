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
The core.utils sub-package provides generic convenience functions and classes
which are used throughout the package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2023 - 2025, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0-only"
__maintainer__ = "Malte Storm"
__status__ = "Production"


# import __all__ items from modules:
from . import scattering_geometry
from .clipboard_ import *
from .decorators import *
from .file_checks import *
from .file_utils import *
from .format_arguments_ import *
from .get_documentation_targets import *
from .hdf5_dataset_utils import *
from .image_utils import *
from .iterable_utils import *
from .logger import *
from .math_utils import *
from .no_print import *
from .numpy_parser import *
from .qt_utilities import *
from .rebin_ import *
from .show_busy_mouse import *
from .sphinx_html import *
from .str_utils import *
from .timer import *


__all__ = (
    clipboard_.__all__
    + decorators.__all__
    + file_checks.__all__
    + file_utils.__all__
    + iterable_utils.__all__
    + format_arguments_.__all__
    + get_documentation_targets.__all__
    + hdf5_dataset_utils.__all__
    + logger.__all__
    + image_utils.__all__
    + math_utils.__all__
    + numpy_parser.__all__
    + no_print.__all__
    + qt_utilities.__all__
    + rebin_.__all__
    + show_busy_mouse.__all__
    + sphinx_html.__all__
    + str_utils.__all__
    + timer.__all__
)

# Clean up the namespace
del (
    clipboard_,
    decorators,
    file_checks,
    file_utils,
    iterable_utils,
    format_arguments_,
    get_documentation_targets,
    hdf5_dataset_utils,
    logger,
    image_utils,
    math_utils,
    numpy_parser,
    no_print,
    qt_utilities,
    rebin_,
    show_busy_mouse,
    sphinx_html,
    str_utils,
    timer,
)
