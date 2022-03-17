# This file is part of pydidas.
#
# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
The core.constantas package defines generic constants which are used
throughout the pydidas package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021-2022, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


# import __all__ items from modules:
from .constants import *
from .file_extensions import *
from .fit_funcs import *
from .generic_param_description import *
from .gui_constants import *
from .q_settings import *
from .qt_presets import *
from .unicode_greek_letters import *


# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import constants
__all__.extend(constants.__all__)
del constants

from . import file_extensions
__all__.extend(file_extensions.__all__)
del file_extensions

from . import fit_funcs
__all__.extend(fit_funcs.__all__)
del fit_funcs

from . import generic_param_description
__all__.extend(generic_param_description.__all__)
del generic_param_description

from . import gui_constants
__all__.extend(gui_constants.__all__)
del gui_constants

from . import q_settings
__all__.extend(q_settings.__all__)
del q_settings

from . import qt_presets
__all__.extend(qt_presets.__all__)
del qt_presets

from . import unicode_greek_letters
__all__.extend(unicode_greek_letters.__all__)
del unicode_greek_letters
