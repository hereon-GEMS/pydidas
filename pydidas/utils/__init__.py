# This file is part of pydidas.

# pydidas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

"""Package with utility functions."""

__author__      = "Malte Storm"
__copyright__   = "Copyright 2021, Malte Storm, Helmholtz-Zentrum Hereon"
__license__ = "GPL-3.0"
__version__ = "0.0.0"
__maintainer__ = "Malte Storm"
__status__ = "Development"
__all__ = []


from . import hdf5_dataset_utils
from .hdf5_dataset_utils import *

from . import file_checks
from .file_checks import *

from . import decorators
from .decorators import *

from . import str_utils
from .str_utils import *

__all__ += hdf5_dataset_utils.__all__
__all__ += file_checks.__all__
__all__ += decorators.__all__
__all__ += str_utils.__all__

# unclutter namespace and delete the references to the modules itself
# as all functions are imported directly
del hdf5_dataset_utils
del file_checks
del decorators
del str_utils
