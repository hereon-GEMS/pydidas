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
The core.utils sub-package provides generic convenience functions and classes
which are used throughout the package.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []

# import __all__ items from modules:
from .decorators import *
from .file_checks import *
from .file_utils import *
from .flatten_list_ import *
from .format_arguments_ import *
from .get_documentation_targets import *
from .get_module_dir import *
from .hdf5_dataset_utils import *
from .logger_ import *
from .signal_blocker import *
from .sphinx_html import *
from .str_utils import *
from .timer import *

# add modules' __all__ items to package's __all__ items and unclutter the
# namespace by deleting the module references:
from . import decorators
__all__.extend(decorators.__all__)
del decorators

from . import file_checks
__all__.extend(file_checks.__all__)
del file_checks

from . import file_utils
__all__.extend(file_utils.__all__)
del file_utils

from . import flatten_list_
__all__.extend(flatten_list_.__all__)
del flatten_list_

from . import format_arguments_
__all__.extend(format_arguments_.__all__)
del format_arguments_

from . import get_documentation_targets
__all__.extend(get_documentation_targets.__all__)
del get_documentation_targets

from . import get_module_dir
__all__.extend(get_module_dir.__all__)
del get_module_dir

from . import hdf5_dataset_utils
__all__.extend(hdf5_dataset_utils.__all__)
del hdf5_dataset_utils

from . import logger_
__all__.extend(logger_.__all__)
del logger_

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
