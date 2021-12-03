# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pydidas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pydidas. If not, see <http://www.gnu.org/licenses/>.

"""
Package with utility functions.
"""

__author__ = "Malte Storm"
__copyright__ = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.1"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


from . import hdf5_dataset_utils
from .hdf5_dataset_utils import *
__all__ += hdf5_dataset_utils.__all__

from . import file_checks
from .file_checks import *
__all__ += file_checks.__all__

from . import decorators
from .decorators import *
__all__ += decorators.__all__

from . import str_utils
from .str_utils import *
__all__ += str_utils.__all__

from . import file_utils
from .file_utils import *
__all__ += file_utils.__all__

from . import _logger
from ._logger import *
__all__ += _logger.__all__

from . import timer
from .timer import *
__all__ += timer.__all__

from . import signal_blocker
from .signal_blocker import *
__all__ += signal_blocker.__all__

from . import data_formatting_utils
from .data_formatting_utils import *
__all__ += data_formatting_utils.__all__

from . import get_module_dir
from .get_module_dir import *
__all__ += get_module_dir.__all__

# unclutter namespace and delete the references to the modules itself
# as all functions are imported directly
del hdf5_dataset_utils
del file_checks
del decorators
del str_utils
del file_utils
del _logger
del timer
del signal_blocker
del data_formatting_utils
del get_module_dir
